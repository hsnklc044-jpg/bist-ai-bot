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
        entry REAL,
        stop REAL,
        target REAL,
        lot INTEGER,
        regime TEXT,
        active INTEGER,
        pnl REAL,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ------------------------------------------------
# TELEGRAM
# ------------------------------------------------
def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, json=payload, timeout=10)
    except:
        pass

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
# PGE
# ------------------------------------------------
def calculate_pge():
    try:
        df = yf.download("^XU100", period="3mo", progress=False)
        if df.empty:
            return 50
        df["rsi"] = calculate_rsi(df["Close"])
        return float(df["rsi"].iloc[-1])
    except:
        return 50

# ------------------------------------------------
# RISK MODEL
# ------------------------------------------------
def get_risk_model(pge):
    if pge < 35:
        return 0.01, 2.0, "DEFANSİF"
    elif pge > 70:
        return 0.03, 1.3, "AGRESİF"
    else:
        return 0.02, 1.5, "NORMAL"

# ------------------------------------------------
# SABAH SİNYAL
# ------------------------------------------------
@app.get("/morning_report")
def morning_report():

    try:
        pge = calculate_pge()
        risk_percent, min_rr, regime = get_risk_model(pge)

        message = f"🚀 ALGORİTMA 11.1\nPGE:{round(pge,2)} | Rejim:{regime}\n\n"

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        for symbol in BIST_SYMBOLS:

            try:
                df = yf.download(symbol, period="3mo", progress=False)

                if df is None or df.empty:
                    continue

                df["rsi"] = calculate_rsi(df["Close"])
                df["ma20"] = df["Close"].rolling(20).mean()
                df["ma50"] = df["Close"].rolling(50).mean()

                latest = df.iloc[-1]

                score = 0
                if latest["rsi"] > 55: score += 20
                if latest["Close"] > latest["ma20"]: score += 20
                if latest["ma20"] > latest["ma50"]: score += 20

                if score < 60:
                    continue

                entry = float(latest["Close"])
                stop = entry * 0.95
                target = entry * 1.10

                risk_per_share = entry - stop
                if risk_per_share <= 0:
                    continue

                rr = (target - entry) / risk_per_share
                if rr < min_rr:
                    continue

                risk_amount = ACCOUNT_SIZE * risk_percent
                lot = int(risk_amount / risk_per_share)

                cursor.execute("""
                INSERT INTO signals (symbol, entry, stop, target, lot, regime, active, pnl, date)
                VALUES (?,?,?,?,?,?,?,0,?)
                """, (
                    symbol,
                    entry,
                    stop,
                    target,
                    lot,
                    regime,
                    1,
                    datetime.now().strftime("%Y-%m-%d")
                ))

                message += f"{symbol} | Entry:{round(entry,2)} Lot:{lot}\n"

            except:
                continue

        conn.commit()
        conn.close()

        send_telegram(message)
        return {"status":"Morning Signals Sent"}

    except Exception as e:
        return {"error": str(e)}

# ------------------------------------------------
# POZİSYON KONTROL
# ------------------------------------------------
@app.get("/check_positions")
def check_positions():

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT id, symbol, entry, stop, target, lot FROM signals WHERE active=1")
        trades = cursor.fetchall()

        total_pnl = 0
        wins = 0
        losses = 0

        for trade in trades:
            id_, symbol, entry, stop, target, lot = trade

            try:
                df = yf.download(symbol, period="5d", progress=False)
                if df.empty:
                    continue

                price = float(df["Close"].iloc[-1])

                if price >= target:
                    pnl = (target - entry) * lot
                    wins += 1
                elif price <= stop:
                    pnl = (stop - entry) * lot
                    losses += 1
                else:
                    continue

                total_pnl += pnl

                cursor.execute("UPDATE signals SET active=0, pnl=? WHERE id=?", (pnl, id_))

            except:
                continue

        conn.commit()
        conn.close()

        total_trades = wins + losses
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

        report = (
            f"📊 PERFORMANS RAPORU\n"
            f"Toplam PnL: {round(total_pnl,2)}\n"
            f"Win Rate: {round(win_rate,2)}%\n"
            f"İşlem Sayısı: {total_trades}"
        )

        send_telegram(report)

        return {"status":"Positions Checked"}

    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    return {"status":"ALGORİTMA 11.1 STABİL PERFORMANS MOTORU AKTİF"}
