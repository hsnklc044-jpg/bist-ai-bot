import os
import sqlite3
import requests
from datetime import datetime
from fastapi import FastAPI
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI()

# ================= CONFIG =================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

DB_FILE = "fund.db"
START_EQUITY = 100000
MAX_OPEN_POSITIONS = 5
RISK_PER_TRADE = 0.02

BIST_SYMBOLS = [
"AKBNK.IS","ARCLK.IS","ASELS.IS","BIMAS.IS","EKGYO.IS",
"ENKAI.IS","EREGL.IS","FROTO.IS","GARAN.IS","GUBRF.IS",
"HEKTS.IS","ISCTR.IS","KCHOL.IS","KOZAL.IS","KOZAA.IS",
"ODAS.IS","PETKM.IS","PGSUS.IS","SAHOL.IS","SASA.IS",
"SISE.IS","TAVHL.IS","TCELL.IS","THYAO.IS","TOASO.IS",
"TUPRS.IS","VAKBN.IS","YKBNK.IS","ALARK.IS","BRISA.IS"
]

# ================= DATABASE =================

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
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(
            url,
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

def atr(df, period=14):
    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Close"].shift())
    low_close = np.abs(df["Low"] - df["Close"].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def calculate_pge():
    try:
        df = yf.download("^XU100", period="3mo", progress=False)
        if df.empty:
            return 50
        df["rsi"] = rsi(df["Close"])
        return float(df["rsi"].iloc[-1])
    except:
        return 50

# ================= EQUITY =================

def get_equity():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM equity ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else START_EQUITY

def update_equity(value):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO equity(value,date) VALUES(?,?)",
        (value, datetime.now().strftime("%Y-%m-%d"))
    )
    conn.commit()
    conn.close()

# ================= MORNING REPORT =================

@app.get("/morning_report")
def morning():

    equity = get_equity()
    pge = calculate_pge()

    if pge < 40:
        rsi_limit = 45
        mom_limit = 0.01
        regime = "AGRESİF"
        atr_stop = 0.8
        atr_target = 1.4
    elif pge > 65:
        rsi_limit = 55
        mom_limit = 0.03
        regime = "DİSİPLİNLİ"
        atr_stop = 1.0
        atr_target = 1.6
    else:
        rsi_limit = 50
        mom_limit = 0.02
        regime = "NORMAL"
        atr_stop = 0.9
        atr_target = 1.5

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM trades WHERE active=1")
    open_positions = c.fetchone()[0]

    message = f"🚀 ALGORİTMA 14.3 ŞEFFAF MOD\nPGE:{round(pge,2)} | {regime}\n\n"

    signals_found = 0

    for symbol in BIST_SYMBOLS:

        if open_positions >= MAX_OPEN_POSITIONS:
            break

        try:
            df = yf.download(symbol, period="3mo", progress=False)
            if df.empty:
                continue

            df["rsi"] = rsi(df["Close"])
            df["atr"] = atr(df)
            df["vol_avg"] = df["Volume"].rolling(20).mean()

            last = df.iloc[-1]
            momentum = (df["Close"].iloc[-1] / df["Close"].iloc[-20]) - 1

            score = 0
            if last["rsi"] > rsi_limit:
                score += 1
            if momentum > mom_limit:
                score += 1
            if last["Volume"] > last["vol_avg"]:
                score += 1

            if score < 1:
                continue

            entry = float(last["Close"])
            stop = entry - (last["atr"] * atr_stop)
            target = entry + (last["atr"] * atr_target)

            risk_per_share = entry - stop
            if risk_per_share <= 0:
                continue

            risk_amount = equity * RISK_PER_TRADE
            lot = int(risk_amount / risk_per_share)

            if lot <= 0:
                continue

            c.execute("""
            INSERT INTO trades(symbol,entry,stop,target,lot,active,pnl,date)
            VALUES(?,?,?,?,?,?,0,?)
            """, (
                symbol, entry, stop, target, lot, 1,
                datetime.now().strftime("%Y-%m-%d")
            ))

            message += f"{symbol} | Entry:{round(entry,2)} Lot:{lot}\n"
            open_positions += 1
            signals_found += 1

        except:
            continue

    conn.commit()
    conn.close()

    if signals_found == 0:
        message += "⚠️ Bugün uygun teknik setup bulunamadı."

    send_telegram(message)
    return {"status": "Morning Signals Sent"}

# ================= ROOT =================

@app.get("/")
def root():
    return {"status": "ALGORİTMA 14.3 ŞEFFAF MOD AKTİF"}
