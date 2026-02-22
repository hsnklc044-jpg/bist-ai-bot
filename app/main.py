import os
import json
import requests
from datetime import datetime
from fastapi import FastAPI
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SIGNAL_FILE = "signals.json"

BIST_SYMBOLS = [
    "ENKAI.IS","EREGL.IS","KCHOL.IS","TCELL.IS","GUBRF.IS",
    "HALKB.IS","ASELS.IS","BIMAS.IS","FROTO.IS","ISCTR.IS",
    "TOASO.IS","YKBNK.IS","ZOREN.IS","AKBNK.IS","GARAN.IS",
    "PETKM.IS","SAHOL.IS","TAVHL.IS","TUPRS.IS","SASA.IS"
]

# ------------------------------------------------
# RSI
# ------------------------------------------------
def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ------------------------------------------------
# TELEGRAM
# ------------------------------------------------
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)

# ------------------------------------------------
# PGE
# ------------------------------------------------
def calculate_pge():
    try:
        data = yf.download("^XU100", period="3mo")
        data["rsi"] = calculate_rsi(data["Close"])
        return round(float(data["rsi"].iloc[-1]),2)
    except:
        return 50.0

# ------------------------------------------------
# ALGORİTMİK SKOR (0–100)
# ------------------------------------------------
def calculate_score(df, pge):
    latest = df.iloc[-1]

    rsi = latest["rsi"]
    ma20 = df["Close"].rolling(20).mean().iloc[-1]
    ma50 = df["Close"].rolling(50).mean().iloc[-1]
    volume = latest["Volume"]
    avg_vol = df["Volume"].rolling(20).mean().iloc[-1]

    score = 0

    # RSI momentum (20 puan)
    if rsi > 55: score += 10
    if rsi > 60: score += 10

    # MA trend (30 puan)
    if latest["Close"] > ma20: score += 15
    if ma20 > ma50: score += 15

    # Hacim (20 puan)
    if volume > avg_vol: score += 20

    # 3 günlük ivme (15 puan)
    momentum = df["Close"].pct_change(3).iloc[-1]
    if momentum > 0.02: score += 15

    # PGE uyumu (15 puan)
    if pge > 50: score += 15

    return round(score,2)

# ------------------------------------------------
# SİNYAL KAYDET
# ------------------------------------------------
def save_signal(symbol, price, score):
    signal = {
        "symbol": symbol,
        "price": price,
        "score": score,
        "date": datetime.now().strftime("%Y-%m-%d")
    }

    try:
        with open(SIGNAL_FILE,"r") as f:
            data = json.load(f)
    except:
        data = []

    data.append(signal)

    with open(SIGNAL_FILE,"w") as f:
        json.dump(data,f,indent=4)

# ------------------------------------------------
# ANA TARAMA
# ------------------------------------------------
def scan_market():

    breakout = []
    pge = calculate_pge()

    for symbol in BIST_SYMBOLS:
        try:
            df = yf.download(symbol, period="6mo")
            if df.empty:
                continue

            df["rsi"] = calculate_rsi(df["Close"])
            latest = df.iloc[-1]

            score = calculate_score(df, pge)

            if score >= 65:
                data = {
                    "symbol": symbol,
                    "close": round(float(latest["Close"]),2),
                    "rsi": round(float(latest["rsi"]),2),
                    "score": score
                }
                breakout.append(data)
                save_signal(symbol, data["close"], score)

        except:
            continue

    return {
        "pge": pge,
        "breakout": breakout
    }

# ------------------------------------------------
# RAPOR
# ------------------------------------------------
@app.get("/morning_report")
def morning_report():

    result = scan_market()

    message = f"""
📊 ALGORİTMA 2.0 RAPOR

📈 PGE: %{result['pge']}
🚀 Güçlü Sinyal: {len(result['breakout'])}

"""

    for stock in result["breakout"]:
        message += f"{stock['symbol']} | RSI:{stock['rsi']} | Skor:{stock['score']}\n"

    send_telegram(message)

    return {"status":"Rapor Gönderildi"}

@app.get("/")
def root():
    return {"status":"ALGORİTMA 2.0 AKTİF"}
