import os
import json
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from flask import Flask
import threading
import time
from datetime import datetime

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

HISTORY_FILE = "history.json"

RISK_PERCENT = 0.02
DAILY_RISK_LIMIT = 0.04
MAX_DRAWDOWN_LIMIT = 20

BIST30 = [
    "AKBNK.IS","ASELS.IS","BIMAS.IS","EREGL.IS",
    "FROTO.IS","GARAN.IS","KCHOL.IS","KOZAL.IS",
    "PETKM.IS","SAHOL.IS","SASA.IS","SISE.IS",
    "TCELL.IS","THYAO.IS","TUPRS.IS"
]

# =============================
# HISTORY
# =============================

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {
            "equity": 100000,
            "peak": 100000,
            "wins": 0,
            "losses": 0,
            "daily_loss": 0,
            "last_day": str(datetime.now().date()),
            "trades": []
        }
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def save_history(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def update_drawdown(data):
    if data["equity"] > data["peak"]:
        data["peak"] = data["equity"]
    dd = (data["peak"] - data["equity"]) / data["peak"] * 100
    return round(dd,2)

# =============================
# TELEGRAM
# =============================

def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

# =============================
# INDICATORS
# =============================

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100/(1+rs))

def atr(df, period=14):
    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Close"].shift())
    low_close = np.abs(df["Low"] - df["Close"].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(period).mean()

# =============================
# ENGINE
# =============================

def process_trade(symbol, entry, stop, target, today):
    data = load_history()

    # Günlük reset
    if data["last_day"] != str(datetime.now().date()):
        data["daily_loss"] = 0
        data["last_day"] = str(datetime.now().date())

    # Günlük risk limiti
    if data["daily_loss"] >= data["equity"] * DAILY_RISK_LIMIT:
        return None

    drawdown = update_drawdown(data)
    if drawdown >= MAX_DRAWDOWN_LIMIT:
        return None

    risk_amount = data["equity"] * RISK_PERCENT
    stop_distance = entry - stop

    if stop_distance <= 0:
        return None

    lot = risk_amount / stop_distance

    pnl = 0
    result = None

    if today["High"] >= target:
        pnl = lot * (target - entry)
        data["wins"] += 1
        result = "WIN ✅"

    elif today["Low"] <= stop:
        pnl = lot * (stop - entry)
        data["losses"] += 1
        data["daily_loss"] += abs(pnl)
        result = "LOSS ❌"
    else:
        return None

    data["equity"] += pnl

    trade = {
        "symbol": symbol,
        "entry": round(entry,2),
        "lot": round(lot,2),
        "pnl": round(pnl,2),
        "result": result,
        "date": str(datetime.now())
    }

    data["trades"].append(trade)
    save_history(data)

    return trade

# =============================
# STRATEGY
# =============================

def check_signal(symbol):
    df = yf.download(symbol, period="3mo", interval="1d", progress=False)
    if df.empty or len(df) < 60:
        return None

    df["EMA50"] = df["Close"].ewm(span=50).mean()
    df["EMA200"] = df["Close"].ewm(span=200).mean()
    df["RSI"] = rsi(df["Close"])
    df["ATR"] = atr(df)

    last = df.iloc[-2]
    today = df.iloc[-1]

    trend_ok = last["EMA50"] > last["EMA200"]
    rsi_ok = last["RSI"] < 40 and today["RSI"] > 40

    if trend_ok and rsi_ok:
        entry = today["Open"]
        stop = entry - today["ATR"]
        target = entry + (2 * (entry - stop))

        return process_trade(symbol, entry, stop, target, today)

    return None

# =============================
# SCAN
# =============================

def run_scan():
    signals = []
    data = load_history()

    for symbol in BIST30:
        try:
            trade = check_signal(symbol)
            if trade:
                signals.append(
                    f"{trade['symbol']} | {trade['result']} | PnL: {trade['pnl']}"
                )
        except:
            continue

    total = data["wins"] + data["losses"]
    winrate = (data["wins"]/total*100) if total>0 else 0
    drawdown = update_drawdown(data)

    msg = "🏦 INSTITUTIONAL MODE 5.0\n\n"

    if signals:
        msg += "\n".join(signals) + "\n\n"
    else:
        msg += "Sinyal yok.\n\n"

    msg += (
        f"💰 Equity: {round(data['equity'],2)}\n"
        f"📊 Winrate: {round(winrate,2)}%\n"
        f"📉 Drawdown: {drawdown}%\n"
        f"📈 Trades: {total}"
    )

    send_telegram(msg)

# =============================
# ROUTES
# =============================

@app.route("/")
def home():
    return "INSTITUTIONAL MODE 5.0 aktif."

@app.route("/scan")
def manual_scan():
    run_scan()
    return "Scan tamamlandı."

@app.route("/equity")
def equity():
    data = load_history()
    drawdown = update_drawdown(data)
    total = data["wins"] + data["losses"]
    winrate = (data["wins"]/total*100) if total>0 else 0

    return (
        f"Equity: {round(data['equity'],2)} | "
        f"Winrate: {round(winrate,2)}% | "
        f"Drawdown: {drawdown}% | "
        f"Trades: {total}"
    )

# =============================
# AUTO RUN
# =============================

def auto_runner():
    while True:
        try:
            run_scan()
        except:
            pass
        time.sleep(3600)

threading.Thread(target=auto_runner, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
