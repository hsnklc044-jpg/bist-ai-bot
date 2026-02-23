import os
import sqlite3
import requests
from datetime import datetime
from fastapi import FastAPI
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

DB_FILE = "fund.db"
START_EQUITY = 100000
BASE_RISK = 0.02
MAX_OPEN_POSITIONS = 5
MAX_DRAWDOWN_LIMIT = 0.10
DAILY_LOSS_LIMIT = 0.03

BIST_SYMBOLS = [
"AKBNK.IS","ARCLK.IS","ASELS.IS","BIMAS.IS","EKGYO.IS",
"ENKAI.IS","EREGL.IS","FROTO.IS","GARAN.IS","GUBRF.IS",
"HEKTS.IS","ISCTR.IS","KCHOL.IS","KOZAL.IS","KOZAA.IS",
"ODAS.IS","PETKM.IS","PGSUS.IS","SAHOL.IS","SASA.IS",
"SISE.IS","TAVHL.IS","TCELL.IS","THYAO.IS","TOASO.IS",
"TUPRS.IS","VAKBN.IS","YKBNK.IS","ALARK.IS","BRISA.IS"
]

# ================= DB =================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS trades(
        id INTEGER PRIMARY KEY,
        symbol TEXT,
        entry REAL,
        stop REAL,
        target REAL,
        lot INTEGER,
        active INTEGER,
        pnl REAL,
        date TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS equity(
        id INTEGER PRIMARY KEY,
        value REAL,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

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
    try:
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    except:
        return pd.Series()

def atr(df, period=14):
    try:
        high_low = df["High"] - df["Low"]
        high_close = abs(df["High"] - df["Close"].shift())
        low_close = abs(df["Low"] - df["Close"].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(period).mean()
    except:
        return pd.Series()

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
    return {"status": "16.2 STABLE BUILD AKTİF"}

# ================= MORNING =================

@app.get("/morning_report")
def morning():

    try:
        message = "🚀 16.2 STABLE BUILD\n"

        for symbol in BIST_SYMBOLS[:5]:  # yük azaltıldı
            df = safe_download(symbol, "3mo")
            if df is None or len(df) < 50:
                continue

            df["rsi"] = rsi(df["Close"])
            df["atr"] = atr(df)

            last = df.iloc[-1]

            if last["rsi"] > 55:
                message += f"{symbol} | Close:{round(last['Close'],2)}\n"

        send_telegram(message)
        return {"status": "Morning Signals Sent"}

    except Exception as e:
        return {"error": str(e)}

# ================= BACKTEST =================

@app.get("/backtest")
def backtest():

    try:
        equity = START_EQUITY
        trades = []

        for symbol in BIST_SYMBOLS[:5]:  # stabilite için azaltıldı

            df = safe_download(symbol, "2y")
            if df is None or len(df) < 100:
                continue

            df["rsi"] = rsi(df["Close"])
            df["atr"] = atr(df)

            for i in range(50, len(df)-5):

                row = df.iloc[i]

                if row["rsi"] < 55:
                    continue

                entry = float(row["Close"])
                stop = entry - row["atr"]
                target = entry + row["atr"]*1.5

                future = df.iloc[i+1:i+6]
                if future.empty:
                    continue

                exit_price = float(future.iloc[-1]["Close"])

                for _, f in future.iterrows():
                    if f["Low"] <= stop:
                        exit_price = stop
                        break
                    if f["High"] >= target:
                        exit_price = target
                        break

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
