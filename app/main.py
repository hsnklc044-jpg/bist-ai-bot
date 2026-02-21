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

@app.get("/")
def root():
    return {"status": "BIST AI HIBRIT KURUMSAL AKTIF"}

def scan_market():
    global last_scan_time, cached_result
    global previous_breakout_count, previous_pge

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

    # 🔥 ALARM MANTIĞI
    if previous_breakout_count is not None:

        # Breakout artışı sadece PGE >= 50 ise
        if len(breakout) > previous_breakout_count and pge >= 50:
            send_telegram(f"🚀 Güçlü Breakout artışı! ({len(breakout)}) PGE:%{pge}")

        # PGE eşik geçişleri
        if previous_pge < 30 and pge >= 30:
            send_telegram(f"📈 PGE 30 üstüne çıktı! (%{pge})")

        if previous_pge < 50 and pge >= 50:
            send_telegram(f"💪 PGE 50 üstüne çıktı! (%{pge})")

        if previous_pge < 70 and pge >= 70:
            send_telegram(f"🚀 PGE 70 üstüne çıktı! (%{pge})")

    previous_breakout_count = len(breakout)
    previous_pge = pge

    result = (pge, breakout, trend, dip)
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
📊 BIST AI HIBRIT PANEL

/scan → Anlık Tarama
/breakout → Breakout
/top3 → En Güçlü 3
/yorum → Piyasa Yorumu
""")

    elif text == "/scan":
        pge, _, _, _ = scan_market()
        send_telegram(f"📊 PGE: %{pge}")

    elif text == "/breakout":
        _, breakout, _, _ = scan_market()
        msg = "🚀 BREAKOUT\n"
        for h in breakout:
            msg += f"{h['symbol']} RSI:{h['rsi']} Skor:{h['score']}\n"
        send_telegram(msg)

    elif text == "/top3":
        _, breakout, trend, dip = scan_market()
        all_stocks = breakout + trend + dip
        top3 = sorted(all_stocks, key=lambda x: x["score"], reverse=True)[:3]
        msg = "🏆 TOP 3\n"
        for h in top3:
            msg += f"{h['symbol']} RSI:{h['rsi']} Skor:{h['score']}\n"
        send_telegram(msg)

    elif text == "/yorum":
        pge, _, _, _ = scan_market()
        send_telegram(f"🧠 PGE: %{pge}")

    return {"ok": True}
