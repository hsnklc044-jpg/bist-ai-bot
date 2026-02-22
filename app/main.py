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

# ------------------------------------------------
# RİSK PARAMETRELERİ
# ------------------------------------------------
ACCOUNT_SIZE = 100000   # TL
RISK_PERCENT = 0.02     # %2 risk

# ------------------------------------------------
# BIST30
# ------------------------------------------------
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
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            price REAL,
            score REAL,
            sqi REAL,
            rr REAL,
            lot INTEGER,
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
# PGE
# ------------------------------------------------
def calculate_pge():
    try:
        data = yf.download("^XU100", period="3mo", progress=False)
        data["rsi"] = calculate_rsi(data["Close"])
        return float(data["rsi"].iloc[-1])
    except:
        return 50

# ------------------------------------------------
# SKOR
# ------------------------------------------------
def calculate_score(df, pge):

    df["rsi"] = calculate_rsi(df["Close"])
    latest = df.iloc[-1]

    ma20 = df["Close"].rolling(20).mean().iloc[-1]
    ma50 = df["Close"].rolling(50).mean().iloc[-1]

    score = 0

    if latest["rsi"] > 55: score += 15
    if latest["Close"] > ma20: score += 15
    if ma20 > ma50: score += 20

    momentum = df["Close"].pct_change(3).iloc[-1]
    if momentum > 0.02: score += 20

    if pge < 30:
        score -= 20
    elif pge < 70:
        score += 10
    else:
        score += 20

    return round(score,2)

# ------------------------------------------------
# SQI
# ------------------------------------------------
def calculate_sqi(df):

    df["rsi"] = calculate_rsi(df["Close"])
    df["atr"] = calculate_atr(df)

    latest = df.iloc[-1]
    ma20 = df["Close"].rolling(20).mean().iloc[-1]
    ma50 = df["Close"].rolling(50).mean().iloc[-1]

    sqi = 50

    if ma20 > ma50:
        sqi += 15

    if 55 < latest["rsi"] < 68:
        sqi += 15
    elif latest["rsi"] > 75:
        sqi -= 10

    volatility = (latest["atr"] / latest["Close"]) * 100
    if volatility < 2:
        sqi += 10
    elif volatility > 4:
        sqi -= 10

    momentum = df["Close"].pct_change(5).iloc[-1]
    if momentum > 0.03:
        sqi += 10

    return max(0, min(100, round(sqi,2)))

# ------------------------------------------------
# RISK / REWARD
# ------------------------------------------------
def calculate_rr(df):

    df["atr"] = calculate_atr(df)
    latest = df.iloc[-1]

    atr = df["atr"].iloc[-1]
    close = latest["Close"]

    stop = close - (1.5 * atr)
    target = close + (2 * atr)

    rr = (target - close) / (close - stop)

    return round(rr,2), round(stop,2), round(target,2)

# ------------------------------------------------
# POZİSYON HESABI
# ------------------------------------------------
def calculate_position_size(entry, stop):
    risk_amount = ACCOUNT_SIZE * RISK_PERCENT
    risk_per_share = entry - stop

    if risk_per_share <= 0:
        return 0

    lot = risk_amount / risk_per_share
    return int(lot)

# ------------------------------------------------
# 3 GÜN FİLTRE
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
# SAVE
# ------------------------------------------------
def save_signal(symbol, price, score, sqi, rr, lot):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO signals (symbol, price, score, sqi, rr, lot, date) VALUES (?,?,?,?,?,?,?)",
        (symbol, price, score, sqi, rr, lot, datetime.now().strftime("%Y-%m-%d"))
    )
    conn.commit()
    conn.close()

# ------------------------------------------------
# SCAN
# ------------------------------------------------
def scan_market():

    breakout = []
    pge = calculate_pge()

    for symbol in BIST_SYMBOLS:
        try:
            df = yf.download(symbol, period="6mo", progress=False)
            if df.empty:
                continue

            score = calculate_score(df, pge)
            sqi = calculate_sqi(df)
            rr, stop, target = calculate_rr(df)

            if score >= 65 and sqi >= 60 and rr >= 1.5 and not recently_sent(symbol):

                latest = df.iloc[-1]
                lot = calculate_position_size(latest["Close"], stop)

                save_signal(symbol, float(latest["Close"]), score, sqi, rr, lot)

                breakout.append({
                    "symbol": symbol,
                    "score": score,
                    "sqi": sqi,
                    "rr": rr,
                    "stop": stop,
                    "target": target,
                    "lot": lot
                })

        except:
            continue

    return breakout, pge

# ------------------------------------------------
# MORNING REPORT
# ------------------------------------------------
@app.get("/morning_report")
def morning_report():

    signals, pge = scan_market()
    regime = "DEFANSİF" if pge < 40 else "MOMENTUM"

    message = f"📊 ALGORİTMA 6.0 RAPOR\n\nPGE: {round(pge,2)}\nRejim: {regime}\n\n"

    for i, s in enumerate(signals,1):
        message += (
            f"{i}️⃣ {s['symbol']}\n"
            f"Skor:{s['score']} | SQI:{s['sqi']} | RR:{s['rr']}\n"
            f"Stop:{s['stop']} | Target:{s['target']}\n"
            f"Lot:{s['lot']} adet\n\n"
        )

    send_telegram(message)
    return {"status":"Sent"}

@app.get("/")
def root():
    return {"status":"ALGORİTMA 6.0 FULL AKTİF"}
