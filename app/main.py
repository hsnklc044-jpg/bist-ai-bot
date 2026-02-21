import os
import time
import requests
import yfinance as yf
from fastapi import FastAPI, Request

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AUTHORIZED_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

# MEMORY
last_scan_time = 0
cached_result = None
previous_breakout_count = None
previous_pge = None
previous_regime = None

CACHE_SECONDS = 300  # 5 dk

BIST30 = [
    "AKBNK.IS","ALARK.IS","ASELS.IS","BIMAS.IS","EKGYO.IS",
    "ENKAI.IS","EREGL.IS","FROTO.IS","GARAN.IS","HEKTS.IS",
    "ISCTR.IS","KCHOL.IS","KRDMD.IS","ODAS.IS","PETKM.IS",
    "PGSUS.IS","SAHOL.IS","SISE.IS","TAVHL.IS","TCELL.IS",
    "THYAO.IS","TOASO.IS","TUPRS.IS","YKBNK.IS","ZOREN.IS",
    "GUBRF.IS","HALKB.IS","KOZAA.IS","KOZAL.IS","SASA.IS"
]

def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": AUTHORIZED_CHAT_ID, "text": text}
    requests.post(url, data=payload)

def detect_regime(pge):
    if pge < 30:
        return "🔴 Savunma"
    elif pge < 50:
        return "🟡 Geçiş"
    elif pge < 70:
        return "🟢 Trend"
    else:
        return "🚀 Momentum"

@app.get("/")
def root():
    return {"status": "BIST AI REJIMLI AKTIF"}

def scan_market():
    global last_scan_time, cached_result
    global previous_breakout_count, previous_pge, previous_regime

    now = time.time()

    # Smart Cache
    if cached_result and now - last_scan_time < CACHE_SECONDS:
        return cached_result

    breakout, trend, dip = [], [], []

    for symbol in BIST30:
        try:
            df = yf.Ticker(symbol).history(period="6mo")
            if df.empty:
                continue

            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()
            df["RSI"] = calculate_rsi(df["Close"])

            latest = df.iloc[-1]
            close = float(latest["Close"])
            rsi = float(latest["RSI"])
            ma20 = float(latest["MA20"])
            ma50 = float(latest["MA50"])

            score = 0
            if close > ma20: score += 2
            if ma20 > ma50: score += 2
            if rsi > 55: score += 2
            if rsi > 60: score += 1

            data = {
                "symbol": symbol.replace(".IS",""),
                "rsi": round(rsi,2),
                "score": score
            }

            if close > ma20 and ma20 > ma50 and rsi > 60:
                breakout.append(data)
            elif close > ma20 and rsi > 48:
                trend.append(data)
            elif 40 < rsi < 48:
                dip.append(data)

            time.sleep(0.4)

        except:
            continue

    pge = round(
        ((len(breakout)*3)+(len(trend)*2)+(len(dip)*1))
        /(len(BIST30)*3)*100,2
    )

    regime = detect_regime(pge)

    # 🔔 REJİM DEĞİŞİM ALARMI
    if previous_regime is not None and regime != previous_regime:
        send_telegram(f"🔄 Rejim değişti: {previous_regime} → {regime} (PGE %{pge})")

    # 🚀 BREAKOUT ALARMI (Rejime göre)
    if previous_breakout_count is not None:

        if regime == "🟢 Trend" and len(breakout) > previous_breakout_count:
            send_telegram(f"🚀 Breakout artışı ({len(breakout)}) - Trend Modu")

        if regime == "🚀 Momentum" and len(breakout) > previous_breakout_count:
            send_telegram(f"🚀 Güçlü Breakout! ({len(breakout)}) - Momentum Modu")

            # Momentum'da Top3 de gönder
            all_stocks = breakout + trend + dip
            top3 = sorted(all_stocks, key=lambda x: x["score"], reverse=True)[:3]
            msg = "🏆 MOMENTUM TOP 3\n"
            for h in top3:
                msg += f"{h['symbol']} RSI:{h['rsi']} Skor:{h['score']}\n"
            send_telegram(msg)

        if regime == "🟡 Geçiş":
            # Sadece RSI>=65 olan breakout bildir
            strong = [b for b in breakout if b["rsi"] >= 65]
            if strong and len(breakout) > previous_breakout_count:
                send_telegram(f"⚡ Güçlü Breakout (Geçiş Modu): {len(strong)} adet")

    previous_breakout_count = len(breakout)
    previous_pge = pge
    previous_regime = regime

    result = (pge, regime, breakout, trend, dip)
    cached_result = result
    last_scan_time = now

    return result

@app.post("/telegram")
async def telegram_webhook(request: Request):

    data = await request.json()

    if "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text","")

    if chat_id != AUTHORIZED_CHAT_ID:
        return {"ok": True}

    if text == "/start":
        send_telegram("""
📊 BIST AI REJİMLİ PANEL

/scan → Anlık Tarama
/breakout → Breakout
/top3 → En Güçlü 3
/yorum → Rejim & PGE
""")

    elif text == "/scan":
        pge, regime, _, _, _ = scan_market()
        send_telegram(f"📊 PGE: %{pge}\n🧭 Rejim: {regime}")

    elif text == "/yorum":
        pge, regime, _, _, _ = scan_market()
        send_telegram(f"🧠 Rejim: {regime}\n📊 PGE: %{pge}")

    elif text == "/breakout":
        _, regime, breakout, _, _ = scan_market()
        msg = f"🚀 BREAKOUT ({regime})\n"
        for h in breakout:
            msg += f"{h['symbol']} RSI:{h['rsi']} Skor:{h['score']}\n"
        send_telegram(msg)

    elif text == "/top3":
        _, regime, breakout, trend, dip = scan_market()
        all_stocks = breakout + trend + dip
        top3 = sorted(all_stocks, key=lambda x: x["score"], reverse=True)[:3]
        msg = f"🏆 TOP 3 ({regime})\n"
        for h in top3:
            msg += f"{h['symbol']} RSI:{h['rsi']} Skor:{h['score']}\n"
        send_telegram(msg)

    return {"ok": True}
