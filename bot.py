import os
import json
import requests
import pandas as pd
import yfinance as yf
import numpy as np
from flask import Flask
from threading import Thread
import time
from datetime import datetime
import traceback

# ===============================
# CONFIG
# ===============================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

RISK_PER_TRADE = 0.01
STARTING_CAPITAL = 100000

OPEN_FILE = "open_positions.json"
CLOSED_FILE = "closed_trades.json"

app = Flask(__name__)

# ===============================
# UTIL
# ===============================

def load_json(file, default):
    if not os.path.exists(file):
        return default
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=10)
    except:
        pass

# ===============================
# DATA
# ===============================

def get_data(symbol, period="6mo"):
    try:
        df = yf.download(symbol, period=period, interval="1d", progress=False)
        if df is None or df.empty:
            return None
        return df
    except:
        return None

# ===============================
# INDICATORS
# ===============================

def add_indicators(df):
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Close"].shift())
    low_close = np.abs(df["Low"] - df["Close"].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    df["ATR"] = ranges.max(axis=1).rolling(14).mean()

    return df

# ===============================
# EQUITY
# ===============================

def calculate_equity():
    closed = load_json(CLOSED_FILE, [])
    equity = STARTING_CAPITAL
    for trade in closed:
        equity += trade["pnl"]
    return round(equity, 2)

# ===============================
# MARKET REGIME
# ===============================

def market_regime():
    df = get_data("XU100.IS")
    if df is None:
        return False
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    last = df.iloc[-1]
    return last["Close"] > last["EMA50"]

# ===============================
# SIGNAL ENGINE
# ===============================

def generate_signal(symbol):

    df = get_data(symbol)
    if df is None or len(df) < 60:
        return None

    df = add_indicators(df)
    last = df.iloc[-1]

    trend = last["EMA20"] > last["EMA50"]
    rsi_ok = 45 < last["RSI"] < 65

    if trend and rsi_ok:

        entry = last["Close"]
        atr = last["ATR"]

        stop = entry - (1.5 * atr)
        target = entry + (2 * (entry - stop))

        risk = entry - stop
        equity = calculate_equity()
        position_size = (equity * RISK_PER_TRADE) / risk

        return {
            "symbol": symbol,
            "entry": round(entry,2),
            "stop": round(stop,2),
            "target": round(target,2),
            "size": int(position_size),
            "date": str(datetime.now())
        }

    return None

# ===============================
# POSITION MANAGEMENT
# ===============================

def check_open_positions():

    open_positions = load_json(OPEN_FILE, [])
    closed_positions = load_json(CLOSED_FILE, [])

    updated_open = []

    for pos in open_positions:

        df = get_data(pos["symbol"], period="1mo")
        if df is None:
            updated_open.append(pos)
            continue

        last = df.iloc[-1]

        if last["High"] >= pos["target"]:
            pnl = (pos["target"] - pos["entry"]) * pos["size"]
            pos["pnl"] = round(pnl,2)
            pos["result"] = "WIN"
            closed_positions.append(pos)

        elif last["Low"] <= pos["stop"]:
            pnl = (pos["stop"] - pos["entry"]) * pos["size"]
            pos["pnl"] = round(pnl,2)
            pos["result"] = "LOSS"
            closed_positions.append(pos)

        else:
            updated_open.append(pos)

    save_json(OPEN_FILE, updated_open)
    save_json(CLOSED_FILE, closed_positions)

# ===============================
# SCAN ENGINE
# ===============================

BIST30 = [
    "AKBNK.IS","ASELS.IS","BIMAS.IS","EREGL.IS",
    "FROTO.IS","GARAN.IS","KCHOL.IS","KOZAL.IS",
    "PETKM.IS","SAHOL.IS","SISE.IS","TCELL.IS",
    "THYAO.IS","TUPRS.IS","YKBNK.IS"
]

def run_scan():

    if not market_regime():
        send_telegram("⚠️ Market Risk OFF - No new trades")
        return

    open_positions = load_json(OPEN_FILE, [])

    for symbol in BIST30:

        if any(p["symbol"] == symbol for p in open_positions):
            continue

        signal = generate_signal(symbol)

        if signal:
            open_positions.append(signal)
            send_telegram(
                f"📈 NEW TRADE\n"
                f"{signal['symbol']}\n"
                f"Giriş: {signal['entry']}\n"
                f"Stop: {signal['stop']}\n"
                f"Hedef: {signal['target']}\n"
                f"Lot: {signal['size']}"
            )

    save_json(OPEN_FILE, open_positions)

# ===============================
# REPORT
# ===============================

def weekly_report():

    closed = load_json(CLOSED_FILE, [])

    if not closed:
        return

    wins = sum(1 for t in closed if t["result"] == "WIN")
    losses = sum(1 for t in closed if t["result"] == "LOSS")
    total = len(closed)

    winrate = (wins / total * 100) if total > 0 else 0
    equity = calculate_equity()

    send_telegram(
        f"📊 WEEKLY REPORT\n"
        f"Trades: {total}\n"
        f"Winrate: {round(winrate,2)}%\n"
        f"Equity: {equity}"
    )

# ===============================
# SCHEDULER
# ===============================

def scheduler():
    while True:
        try:
            check_open_positions()
            run_scan()

            # Haftada bir rapor (Pazar)
            if datetime.now().weekday() == 6:
                weekly_report()

        except:
            print(traceback.format_exc())

        time.sleep(3600)

# ===============================
# FLASK
# ===============================

@app.route("/")
def home():
    return "INSTITUTIONAL TRACKING MODE ACTIVE"

if __name__ == "__main__":
    send_telegram("🚀 INSTITUTIONAL TRACKING MODE AKTIF")
    Thread(target=scheduler, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
