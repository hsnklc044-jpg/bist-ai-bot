import os
import requests
from datetime import datetime
from fastapi import FastAPI
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BIST_SYMBOLS = [
"AKBNK.IS","ARCLK.IS","ASELS.IS","BIMAS.IS","EKGYO.IS",
"ENKAI.IS","EREGL.IS","FROTO.IS","GARAN.IS","GUBRF.IS"
]

# ================= TELEGRAM =================

def send_telegram(msg):
    try:
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": msg},
                timeout=10
            )
    except:
        pass

# ================= INDICATORS =================

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ================= SAFE DOWNLOAD =================

def safe_download(symbol, period):
    try:
        df = yf.download(symbol, period=period, progress=False)
        if df is None or df.empty:
            return None
        return df
    except:
        return None

# ================= ROOT =================

@app.get("/")
def root():
    return {"status": "16.3 FIX BUILD AKTİF"}

# ================= MORNING =================

@app.get("/morning_report")
def morning():

    try:
        message = "🚀 16.3 FIX BUILD\n"

        for symbol in BIST_SYMBOLS:

            df = safe_download(symbol, "3mo")
            if df is None or len(df) < 50:
                continue

            df["rsi"] = rsi(df["Close"])

            last = df.iloc[-1]

            rsi_value = float(last["rsi"]) if not pd.isna(last["rsi"]) else None

            if rsi_value is None:
                continue

            if rsi_value > 55:
                close_price = float(last["Close"])
                message += f"{symbol} | Close:{round(close_price,2)} RSI:{round(rsi_value,2)}\n"

        send_telegram(message)
        return {"status": "Morning Signals Sent"}

    except Exception as e:
        return {"error": str(e)}

# ================= BACKTEST =================

@app.get("/backtest")
def backtest():

    try:
        equity = 100000
        trades = []

        for symbol in BIST_SYMBOLS:

            df = safe_download(symbol, "2y")
            if df is None or len(df) < 100:
                continue

            df["rsi"] = rsi(df["Close"])

            for i in range(50, len(df)-5):

                rsi_val = df["rsi"].iloc[i]

                if pd.isna(rsi_val):
                    continue

                rsi_val = float(rsi_val)

                if rsi_val < 55:
                    continue

                entry = float(df["Close"].iloc[i])
                exit_price = float(df["Close"].iloc[i+5])

                pnl = exit_price - entry
                equity += pnl
                trades.append(pnl)

        if not trades:
            return {"result": "Trade oluşmadı"}

        wins = [t for t in trades if t > 0]
        win_rate = len(wins)/len(trades)*100

        return {
            "final_equity": round(equity,2),
            "trades": len(trades),
            "win_rate": round(win_rate,2)
        }

    except Exception as e:
        return {"error": str(e)}
