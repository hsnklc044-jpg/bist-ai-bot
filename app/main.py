import os
import sqlite3
import requests
from datetime import datetime
from fastapi import FastAPI
import yfinance as yf
import pandas as pd

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

DB_FILE = "signals.db"

ACCOUNT_SIZE = 100000
RISK_PERCENT = 0.02
MAX_POSITIONS = 3

BIST_SYMBOLS = [
    "AKBNK.IS","ARCLK.IS","ASELS.IS","BIMAS.IS","EKGYO.IS",
    "ENKAI.IS","EREGL.IS","FROTO.IS","GARAN.IS","GUBRF.IS",
    "HEKTS.IS","ISCTR.IS","KCHOL.IS","KOZAL.IS","KOZAA.IS",
    "ODAS.IS","PETKM.IS","PGSUS.IS","SAHOL.IS","SASA.IS",
    "SISE.IS","TAVHL.IS","TCELL.IS","THYAO.IS","TOASO.IS",
    "TUPRS.IS","VAKBN.IS","YKBNK.IS","ALARK.IS","BRISA.IS"
]

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            price REAL,
            score REAL,
            sqi REAL,
            rr REAL,
            lot INTEGER,
            active INTEGER,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def active_positions():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM signals WHERE active=1")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def save_signal(symbol, price, score, sqi, rr, lot):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO signals (symbol, price, score, sqi, rr, lot, active, date) VALUES (?,?,?,?,?,?,?,?)",
        (symbol, price, score, sqi, rr, lot, 1, datetime.now().strftime("%Y-%m-%d"))
    )
    conn.commit()
    conn.close()

def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_atr(df, period=14):
    df["H-L"] = df["High"] - df["Low"]
    df["H-C"] = abs(df["High"] - df["Close"].shift())
    df["L-C"] = abs(df["Low"] - df["Close"].shift())
    tr = df[["H-L","H-C","L-C"]].max(axis=1)
    return tr.rolling(period).mean()

def calculate_position_size(entry, stop):
    risk_amount = ACCOUNT_SIZE * RISK_PERCENT
    risk_per_share = entry - stop
    if risk_per_share <= 0:
        return 0
    return int(risk_amount / risk_per_share)

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)

def scan_market():

    if active_positions() >= MAX_POSITIONS:
        return [], "PORTFÖY DOLU"

    breakout = []

    for symbol in BIST_SYMBOLS:
        try:
            df = yf.download(symbol, period="6mo", progress=False)
            if df.empty:
                continue

            df["rsi"] = calculate_rsi(df["Close"])
            df["atr"] = calculate_atr(df)

            latest = df.iloc[-1]
            ma20 = df["Close"].rolling(20).mean().iloc[-1]
            ma50 = df["Close"].rolling(50).mean().iloc[-1]

            score = 0
            if latest["rsi"] > 55: score += 20
            if latest["Close"] > ma20: score += 20
            if ma20 > ma50: score += 20

            stop = latest["Close"] - (1.5 * latest["atr"])
            target = latest["Close"] + (2 * latest["atr"])
            rr = (target - latest["Close"]) / (latest["Close"] - stop)

            if score >= 60 and rr >= 1.5:

                lot = calculate_position_size(latest["Close"], stop)
                save_signal(symbol, float(latest["Close"]), score, 60, rr, lot)

                breakout.append({
                    "symbol": symbol,
                    "score": score,
                    "rr": round(rr,2),
                    "lot": lot
                })

                if len(breakout) >= MAX_POSITIONS:
                    break

        except:
            continue

    return breakout, "AKTİF"

@app.get("/morning_report")
def morning_report():

    signals, status = scan_market()

    message = f"📊 ALGORİTMA 7.0\nDurum: {status}\n\n"

    for s in signals:
        message += (
            f"{s['symbol']} | Skor:{s['score']} | RR:{s['rr']}\n"
            f"Lot:{s['lot']}\n\n"
        )

    send_telegram(message)
    return {"status":"Sent"}

@app.get("/")
def root():
    return {"status":"ALGORİTMA 7.0 PORTFÖY LİMİTLİ AKTİF"}
