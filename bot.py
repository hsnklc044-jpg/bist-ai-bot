import os
import requests
import pandas as pd
import yfinance as yf
import numpy as np
from flask import Flask
from threading import Thread
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)

# ==============================
# TELEGRAM
# ==============================

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# ==============================
# DATA ENGINE (CRASH PROOF)
# ==============================

def get_data(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if df is None or df.empty:
            print(f"{symbol} veri yok.")
            return None
        return df
    except Exception as e:
        print(f"{symbol} hata:", e)
        return None

# ==============================
# INDICATORS
# ==============================

def calculate_indicators(df):
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df["VOL"] = df["Close"].rolling(20).std()

    return df

# ==============================
# SIGNAL LOGIC (INSTITUTIONAL)
# ==============================

def generate_signal(df):
    if len(df) < 60:
        return None

    last = df.iloc[-1]

    trend = last["EMA20"] > last["EMA50"]
    rsi_ok = 40 < last["RSI"] < 65
    volatility_ok = last["VOL"] < df["VOL"].mean() * 1.5
    momentum = df["Close"].iloc[-1] > df["Close"].iloc[-5]

    score = sum([trend, rsi_ok, volatility_ok, momentum])

    if score >= 3:
        return {
            "price": last["Close"],
            "score": score
        }

    return None

# ==============================
# BIST UNIVERSE
# ==============================

BIST30 = [
    "AKBNK.IS","ARCLK.IS","ASELS.IS","BIMAS.IS","EREGL.IS",
    "FROTO.IS","GARAN.IS","HEKTS.IS","ISCTR.IS","KCHOL.IS",
    "KOZAL.IS","KOZAA.IS","PETKM.IS","PGSUS.IS","SAHOL.IS",
    "SISE.IS","TAVHL.IS","TCELL.IS","THYAO.IS","TOASO.IS",
    "TUPRS.IS","YKBNK.IS"
]

# ==============================
# SCAN ENGINE
# ==============================

def run_scan():
    print("Scan started")
    signals = []

    for symbol in BIST30:
        df = get_data(symbol)
        if df is None:
            continue

        df = calculate_indicators(df)
        signal = generate_signal(df)

        if signal:
            signals.append((symbol, signal))

    if signals:
        message = "<b>🔥 HEDGE FUND MODE 3.0 SIGNAL</b>\n\n"
        for s in signals:
            message += f"<b>{s[0]}</b>\n"
            message += f"Fiyat: {round(s[1]['price'],2)}\n"
            message += f"Score: {s[1]['score']}/4\n\n"

        send_telegram(message)
    else:
        send_telegram("ULTRA STABLE BIST BOT aktif\nSinyal yok.\nEquity korunuyor.")

# ==============================
# BACKGROUND LOOP
# ==============================

def scheduler():
    while True:
        try:
            run_scan()
        except Exception as e:
            print("Scan crash prevented:", e)
        time.sleep(3600)  # 1 saat

# ==============================
# FLASK KEEP ALIVE
# ==============================

@app.route("/")
def home():
    return "BIST AI BOT ACTIVE"

if __name__ == "__main__":
    send_telegram("🚀 HEDGE FUND MODE 3.0 AKTIF")
    Thread(target=scheduler).start()
    app.run(host="0.0.0.0", port=8080)
