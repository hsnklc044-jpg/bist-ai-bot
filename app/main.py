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
BASE_RISK = 0.02
MAX_OPEN_POSITIONS = 5
MAX_DRAWDOWN_LIMIT = 0.10
DAILY_LOSS_LIMIT = 0.03   # %3 kill switch

# ================= SYMBOLS =================

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

# ================= HELPERS =================

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

# ================= EQUITY =================

def get_equity_curve():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM equity ORDER BY id ASC")
    data = c.fetchall()
    conn.close()
    return [d[0] for d in data] if data else [START_EQUITY]

def get_current_equity():
    return get_equity_curve()[-1]

def update_equity(value):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO equity(value,date) VALUES(?,?)",
              (value, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

def calculate_drawdown():
    curve = get_equity_curve()
    peak = curve[0]
    max_dd = 0
    for val in curve:
        if val > peak:
            peak = val
        dd = (peak - val) / peak
        if dd > max_dd:
            max_dd = dd
    return max_dd

# ================= TRAILING STOP =================

def update_trailing_stops():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id,symbol,entry,stop,lot FROM trades WHERE active=1")
    trades = c.fetchall()

    for t in trades:
        id_, symbol, entry, stop, lot = t
        df = yf.download(symbol, period="1mo", progress=False)
        if df.empty:
            continue

        df["atr"] = atr(df)
        last = df.iloc[-1]
        price = float(last["Close"])

        # Stop'u yukarı taşı
        new_stop = price - (last["atr"] * 0.8)

        if new_stop > stop:
            c.execute("UPDATE trades SET stop=? WHERE id=?",
                      (new_stop, id_))

    conn.commit()
    conn.close()

# ================= MORNING =================

@app.get("/morning_report")
def morning():

    equity = get_current_equity()
    drawdown = calculate_drawdown()

    # Kill switch kontrol
    today_loss = 0
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT pnl FROM trades WHERE date=? AND active=0", (today,))
    rows = c.fetchall()
    conn.close()

    if rows:
        today_loss = sum([r[0] for r in rows if r[0] < 0])

    if abs(today_loss) >= equity * DAILY_LOSS_LIMIT:
        send_telegram("🛑 GÜNLÜK KILL SWITCH AKTİF - Yeni işlem açılmayacak.")
        return {"status": "Kill Switch Active"}

    # Trailing güncelle
    update_trailing_stops()

    return {"status": "System Running - Trailing Updated"}

# ================= ROOT =================

@app.get("/")
def root():
    return {"status": "ALGORİTMA 16.0 TRAILING + KILL SWITCH AKTİF"}
