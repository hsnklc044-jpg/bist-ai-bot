import os
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from flask import Flask
import threading
import time
from datetime import datetime

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BIST30 = [
    "AKBNK.IS","ASELS.IS","BIMAS.IS","EREGL.IS",
    "FROTO.IS","GARAN.IS","KCHOL.IS","KOZAL.IS",
    "PETKM.IS","SAHOL.IS","SASA.IS","SISE.IS",
    "TCELL.IS","THYAO.IS","TUPRS.IS"
]

# ================================
# TELEGRAM
# ================================

def send_telegram(message):
    if not TOKEN or not CHAT_ID:
        print("Telegram bilgileri eksik.")
        return
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram hata:", e)

# ================================
# STRATEJİ
# ================================

def check_signal(symbol):
    df = yf.download(symbol, period="3mo", interval="1d", progress=False)

    if df.empty or len(df) < 50:
        return None

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    last = df.iloc[-1]

    if last["EMA20"] > last["EMA50"]:
        return "AL"
    elif last["EMA20"] < last["EMA50"]:
        return "SAT"
    
    return None

# ================================
# SCAN
# ================================

def run_scan():
    print("Scan başladı:", datetime.now())

    signals = []

    for symbol in BIST30:
        try:
            signal = check_signal(symbol)
            if signal:
                signals.append(f"{symbol} → {signal}")
        except Exception as e:
            print("Hata:", symbol, e)

    if signals:
        message = "🚀 ULTRA STABLE BIST BOT\n\n"
        message += "\n".join(signals)
    else:
        message = "📊 ULTRA STABLE BIST BOT\n\nSinyal yok."

    send_telegram(message)

# ================================
# EQUITY
# ================================

@app.route("/equity")
def equity():
    return "Equity: 100000 | PnL: 0 | Win Rate: 0%"

# ================================
# MANUEL SCAN ENDPOINT
# ================================

@app.route("/scan")
def scan_endpoint():
    run_scan()
    return "Scan tamamlandı."

# ================================
# ANA SAYFA
# ================================

@app.route("/")
def home():
    return "ULTRA STABLE BIST BOT aktif."

# ================================
# OTOMATİK SCHEDULER
# ================================

def auto_runner():
    while True:
        try:
            run_scan()
        except Exception as e:
            print("Auto scan error:", e)
        time.sleep(3600)  # 1 saat

threading.Thread(target=auto_runner, daemon=True).start()

# ================================
# RAILWAY START
# ================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
