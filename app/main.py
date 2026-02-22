# ⚠️ UZUN KOD — TAMAMINI YAPIŞTIR
import os
import time
import requests
import yfinance as yf
from fastapi import FastAPI, Request

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AUTHORIZED_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

CACHE_SECONDS = 300
ALARM_COOLDOWN = 1800  # 30 dakika

last_scan_time = 0
cached_result = None
previous_breakout_count = None
previous_regime = None
previous_pge = None
last_alarm_time = 0

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
    return {"status": "BIST AI FULL PROFESYONEL AKTIF"}

@app.get("/morning_report")
def morning_report():
    pge, regime, breakout, trend, dip = scan_market()
    send_telegram(
        f"🌅 AÇILIŞ RAPORU\n"
        f"🧭 Rejim: {regime}\n"
        f"📊 PGE: %{pge}\n"
        f"🚀 Breakout: {len(breakout)}"
    )
    return {"status": "Morning sent"}

@app.get("/evening_report")
def evening_report():
    pge, regime, breakout, trend, dip = scan_market()
    send_telegram(
        f"🌆 GÜN SONU RAPORU\n"
        f"🧭 Rejim: {regime}\n"
        f"📊 PGE: %{pge}\n"
        f"🚀 Breakout: {len(breakout)}\n"
        f"📈 Trend: {len(trend)}\n"
        f"🔄 Dip: {len(dip)}"
    )
    return {"status": "Evening sent"}

def scan_market():
    global last_scan_time, cached_result
    global previous_breakout_count, previous_regime
    global previous_pge, last_alarm_time

    now = time.time()

    if cached_result and now - last_scan_time < CACHE_SECONDS:
        return cached_result

    breakout, trend, dip = [], [], []

    for symbol in BIST30:
        try:
            df = yf.Ticker(symbol).history(period="6mo")
            if df.empty or len(df) < 50:
                continue

            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()
            df["RSI"] = calculate_rsi(df["Close"])
            df["AVG_VOL"] = df["Volume"].rolling(20).mean()

            latest = df.iloc[-1]
            close = float(latest["Close"])
            rsi = float(latest["RSI"])
            ma20 = float(latest["MA20"])
            ma50 = float(latest["MA50"])
            volume = float(latest["Volume"])
            avg_volume = float(latest["AVG_VOL"])

            score = 0
            if close > ma20: score += 2
            if ma20 > ma50: score += 2
            if rsi > 55: score += 2
            if rsi > 60: score += 1
            if volume > avg_volume: score += 2

            data = {
                "symbol": symbol.replace(".IS",""),
                "rsi": round(rsi,2),
                "score": score
            }

            if close > ma20 and ma20 > ma50 and rsi > 60 and volume > avg_volume:
                breakout.append(data)
            elif close > ma20 and rsi > 48:
                trend.append(data)
            elif 40 < rsi < 48:
                dip.append(data)

            time.sleep(0.4)

        except:
            continue

    pge = round(((len(breakout)*3)+(len(trend)*2)+(len(dip))) / (len(BIST30)*3)*100,2)
    regime = detect_regime(pge)

    # 🔔 PGE kritik alarm
    if previous_pge is not None:
        if previous_pge < 50 and pge >= 50:
            send_telegram("📈 PGE 50 üstüne çıktı!")
        if previous_pge < 70 and pge >= 70:
            send_telegram("🚀 PGE 70 geçti! Momentum başlıyor!")
        if previous_pge > 30 and pge <= 30:
            send_telegram("⚠️ PGE 30 altına düştü! Savunma modu!")

    # 🚀 Breakout alarm + cooldown
    if previous_breakout_count is not None:
        if len(breakout) > previous_breakout_count:
            if now - last_alarm_time > ALARM_COOLDOWN:
                send_telegram(f"🚀 Breakout artışı: {len(breakout)}")
                last_alarm_time = now

    previous_breakout_count = len(breakout)
    previous_regime = regime
    previous_pge = pge

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

    if text == "/scan":
        pge, regime, _, _, _ = scan_market()
        send_telegram(f"📊 PGE: %{pge}\n🧭 Rejim: {regime}")

    return {"ok": True}
