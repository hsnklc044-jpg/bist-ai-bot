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

BIST_SYMBOLS = [
    "ENKAI.IS","EREGL.IS","KCHOL.IS","TCELL.IS","GUBRF.IS",
    "HALKB.IS","ASELS.IS","BIMAS.IS","FROTO.IS","ISCTR.IS",
    "TOASO.IS","YKBNK.IS","ZOREN.IS","AKBNK.IS","GARAN.IS",
    "PETKM.IS","SAHOL.IS","TAVHL.IS","TUPRS.IS","SASA.IS"
]

# ------------------------------------------------
# DB INIT
# ------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            price REAL,
            score REAL,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

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
# ATR
# ------------------------------------------------
def calculate_atr(df, period=14):
    df["H-L"] = df["High"] - df["Low"]
    df["H-C"] = abs(df["High"] - df["Close"].shift())
    df["L-C"] = abs(df["Low"] - df["Close"].shift())
    tr = df[["H-L","H-C","L-C"]].max(axis=1)
    return tr.rolling(period).mean()

# ------------------------------------------------
# TELEGRAM
# ------------------------------------------------
def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)

# ------------------------------------------------
# RECENT CHECK
# ------------------------------------------------
def recently_sent(symbol):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT date FROM signals WHERE symbol=? ORDER BY id DESC LIMIT 1",(symbol,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False

    last_date = datetime.strptime(row[0], "%Y-%m-%d")
    return (datetime.now() - last_date).days <= 3

# ------------------------------------------------
# SAVE SIGNAL
# ------------------------------------------------
def save_signal(symbol, price, score):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO signals (symbol, price, score, date) VALUES (?,?,?,?)",
        (symbol, price, score, datetime.now().strftime("%Y-%m-%d"))
    )
    conn.commit()
    conn.close()

# ------------------------------------------------
# SCORE
# ------------------------------------------------
def calculate_score(df):
    latest = df.iloc[-1]

    df["rsi"] = calculate_rsi(df["Close"])
    df["atr"] = calculate_atr(df)

    rsi = latest["rsi"]
    ma20 = df["Close"].rolling(20).mean().iloc[-1]
    ma50 = df["Close"].rolling(50).mean().iloc[-1]

    score = 0

    if rsi > 55: score += 15
    if latest["Close"] > ma20: score += 15
    if ma20 > ma50: score += 20

    momentum = df["Close"].pct_change(3).iloc[-1]
    if momentum > 0.02: score += 20

    return score

# ------------------------------------------------
# SCAN
# ------------------------------------------------
def scan_market():
    breakout = []

    for symbol in BIST_SYMBOLS:
        try:
            df = yf.download(symbol, period="6mo", progress=False)
            if df.empty:
                continue

            score = calculate_score(df)

            if score >= 65 and not recently_sent(symbol):
                latest = df.iloc[-1]
                save_signal(symbol, float(latest["Close"]), score)

                breakout.append({
                    "symbol": symbol,
                    "score": score
                })

        except:
            continue

    return breakout

# ------------------------------------------------
# MORNING REPORT
# ------------------------------------------------
@app.get("/morning_report")
def morning_report():
    signals = scan_market()

    message = f"📊 ALGORİTMA 5.0 RAPOR\n\nSinyal Sayısı: {len(signals)}\n\n"

    for s in signals:
        message += f"{s['symbol']} | Skor:{s['score']}\n"

    send_telegram(message)
    return {"status":"Sent"}

# ------------------------------------------------
# ROOT
# ------------------------------------------------
@app.get("/")
def root():
    return {"status":"ALGORİTMA 5.0 SQLITE AKTİF"}
