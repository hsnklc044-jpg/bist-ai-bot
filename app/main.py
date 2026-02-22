import os
import requests
from fastapi import FastAPI
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BIST_SYMBOLS = [
    "ENKAI.IS","EREGL.IS","KCHOL.IS","TCELL.IS","GUBRF.IS",
    "HALKB.IS","ASELS.IS","BIMAS.IS","FROTO.IS","ISCTR.IS",
    "TOASO.IS","YKBNK.IS","ZOREN.IS","AKBNK.IS","GARAN.IS",
    "PETKM.IS","SAHOL.IS","TAVHL.IS","TUPRS.IS","SASA.IS"
]

# ------------------------------------------------
# RSI HESAPLAMA
# ------------------------------------------------
def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ------------------------------------------------
# TELEGRAM GÖNDER
# ------------------------------------------------
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, json=payload)

# ------------------------------------------------
# PİYASA GÜÇ ENDEKSİ (PGE)
# ------------------------------------------------
def calculate_pge():
    try:
        data = yf.download("^XU100", period="3mo")
        data["rsi"] = calculate_rsi(data["Close"])
        pge = round(float(data["rsi"].iloc[-1]), 2)
        return pge
    except:
        return 50.0

# ------------------------------------------------
# ANA TARAMA
# ------------------------------------------------
def scan_market():
    breakout = []
    dip = []
    trend = []
    hata = 0

    pge = calculate_pge()

    for symbol in BIST_SYMBOLS:
        try:
            df = yf.download(symbol, period="6mo")
            if df.empty:
                continue

            df["rsi"] = calculate_rsi(df["Close"])
            rsi = round(float(df["rsi"].iloc[-1]), 2)
            close = round(float(df["Close"].iloc[-1]), 2)

            score = 0
            if rsi > 60: score += 2
            if rsi > 65: score += 2
            if rsi > 70: score += 2
            if close > df["Close"].rolling(20).mean().iloc[-1]: score += 1

            # -----------------------------------------
            # REJİM + KURUMSAL FİLTRE
            # -----------------------------------------

            # BREAKOUT
            if (
                55 <= rsi <= 70 and
                score >= 6 and
                pge >= 30
            ):
                breakout.append({"symbol": symbol, "close": close, "rsi": rsi})

            # DIP
            if (
                35 <= rsi <= 45 and
                score >= 4 and
                pge <= 60
            ):
                dip.append({"symbol": symbol, "close": close, "rsi": rsi})

            # TREND
            if (
                rsi >= 60 and
                score >= 6 and
                pge >= 40
            ):
                trend.append({"symbol": symbol, "close": close, "rsi": rsi})

        except:
            hata += 1

    return {
        "pge": pge,
        "breakout": breakout,
        "dip": dip,
        "trend": trend,
        "hata": hata
    }

# ------------------------------------------------
# MORNING REPORT
# ------------------------------------------------
@app.get("/morning_report")
def morning_report():

    now = datetime.now()
    if now.hour < 9:
        return {"status": "Saat dışı"}

    result = scan_market()

    message = f"""
📊 BIST AI KURUMSAL RAPOR

📈 PGE: %{result['pge']}

🚀 Breakout: {len(result['breakout'])}
📉 Dip: {len(result['dip'])}
📊 Trend: {len(result['trend'])}

"""

    send_telegram(message)
    return {"status": "Sabah Rapor Gönderildi"}

# ------------------------------------------------
# EVENING REPORT
# ------------------------------------------------
@app.get("/evening_report")
def evening_report():

    now = datetime.now()
    if now.hour < 18:
        return {"status": "Saat dışı"}

    result = scan_market()

    message = f"""
🌆 AKŞAM KAPANIŞ RAPORU

📈 PGE: %{result['pge']}

🚀 Breakout: {len(result['breakout'])}
📉 Dip: {len(result['dip'])}
📊 Trend: {len(result['trend'])}

"""

    send_telegram(message)
    return {"status": "Akşam Rapor Gönderildi"}

# ------------------------------------------------
# ROOT
# ------------------------------------------------
@app.get("/")
def root():
    return {"status": "BIST AI KURUMSAL AKTİF"}
