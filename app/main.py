import os
import sqlite3
import requests
from datetime import datetime
from fastapi import FastAPI
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

DB_FILE = "signals.db"

ACCOUNT_SIZE = 100000
RISK_PERCENT = 0.02
MAX_WORKERS = 6

BIST_SYMBOLS = [
    "AKBNK.IS","ARCLK.IS","ASELS.IS","BIMAS.IS","EKGYO.IS",
    "ENKAI.IS","EREGL.IS","FROTO.IS","GARAN.IS","GUBRF.IS",
    "HEKTS.IS","ISCTR.IS","KCHOL.IS","KOZAL.IS","KOZAA.IS",
    "ODAS.IS","PETKM.IS","PGSUS.IS","SAHOL.IS","SASA.IS",
    "SISE.IS","TAVHL.IS","TCELL.IS","THYAO.IS","TOASO.IS",
    "TUPRS.IS","VAKBN.IS","YKBNK.IS","ALARK.IS","BRISA.IS"
]

# ------------------------------------------------
# DB INIT
# ------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS market_data (
        symbol TEXT,
        close REAL,
        rsi REAL,
        ma20 REAL,
        ma50 REAL,
        atr REAL,
        date TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        entry REAL,
        stop REAL,
        target REAL,
        lot INTEGER,
        active INTEGER,
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
# DATA UPDATE (PARALEL)
# ------------------------------------------------
def fetch_symbol(symbol):
    try:
        df = yf.download(symbol, period="3mo", progress=False)
        if df.empty:
            return None

        df["rsi"] = calculate_rsi(df["Close"])
        df["ma20"] = df["Close"].rolling(20).mean()
        df["ma50"] = df["Close"].rolling(50).mean()
        df["atr"] = calculate_atr(df)

        latest = df.iloc[-1]

        return (
            symbol,
            float(latest["Close"]),
            float(latest["rsi"]),
            float(latest["ma20"]),
            float(latest["ma50"]),
            float(latest["atr"]),
            datetime.now().strftime("%Y-%m-%d")
        )

    except:
        return None

@app.get("/update_data")
def update_data():

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM market_data")
    conn.commit()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(fetch_symbol, s) for s in BIST_SYMBOLS]

        for future in as_completed(futures):
            result = future.result()
            if result:
                cursor.execute("INSERT INTO market_data VALUES (?,?,?,?,?,?,?)", result)

    conn.commit()
    conn.close()

    return {"status": "DATA UPDATED"}

# ------------------------------------------------
# POZİSYON BOYUTU
# ------------------------------------------------
def calculate_position_size(entry, stop):
    risk_amount = ACCOUNT_SIZE * RISK_PERCENT
    risk_per_share = entry - stop
    if risk_per_share <= 0:
        return 0
    return int(risk_amount / risk_per_share)

# ------------------------------------------------
# SABAH RAPORU (SİNYAL ÜRETİR)
# ------------------------------------------------
@app.get("/morning_report")
def morning_report():

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM market_data")
    rows = cursor.fetchall()

    message = "🚀 ALGORİTMA 9.0 RAPOR\n\n"

    for row in rows:
        symbol, close, rsi, ma20, ma50, atr, _ = row

        score = 0
        if rsi > 55: score += 20
        if close > ma20: score += 20
        if ma20 > ma50: score += 20

        stop = close - (1.5 * atr)
        target = close + (2 * atr)
        rr = (target - close) / (close - stop)

        if score >= 60 and rr >= 1.5:

            lot = calculate_position_size(close, stop)

            cursor.execute("""
            INSERT INTO signals (symbol, entry, stop, target, lot, active, date)
            VALUES (?,?,?,?,?,?,?)
            """, (
                symbol,
                close,
                stop,
                target,
                lot,
                1,
                datetime.now().strftime("%Y-%m-%d")
            ))

            message += f"{symbol}\nEntry:{round(close,2)}\nStop:{round(stop,2)}\nTarget:{round(target,2)}\nLot:{lot}\n\n"

    conn.commit()
    conn.close()

    send_telegram(message)
    return {"status":"Sent"}

# ------------------------------------------------
# TRAILING STOP & YÖNETİM
# ------------------------------------------------
@app.get("/manage_positions")
def manage_positions():

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT id, symbol, entry, stop, target, lot FROM signals WHERE active=1")
    positions = cursor.fetchall()

    message = "📊 POZİSYON YÖNETİMİ\n\n"

    for pos in positions:
        pid, symbol, entry, stop, target, lot = pos

        df = yf.download(symbol, period="5d", progress=False)
        current_price = float(df["Close"].iloc[-1])

        # 1️⃣ Kâr kilidi
        if current_price > entry * 1.03:
            stop = entry

        # 2️⃣ Trailing
        if current_price > target:
            stop = current_price - (0.5 * (target - entry))

        # 3️⃣ Stop kırıldıysa kapat
        if current_price <= stop:
            cursor.execute("UPDATE signals SET active=0 WHERE id=?", (pid,))
            message += f"{symbol} STOP ÇALIŞTI\n\n"
        else:
            cursor.execute("UPDATE signals SET stop=? WHERE id=?", (stop, pid))
            message += f"{symbol} Güncel Stop:{round(stop,2)}\n\n"

    conn.commit()
    conn.close()

    send_telegram(message)
    return {"status":"Managed"}

@app.get("/")
def root():
    return {"status":"ALGORİTMA 9.0 TRAILING STOP AKTİF"}
