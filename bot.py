import os
import json
import requests
import yfinance as yf
import pandas as pd
from flask import Flask
import threading
import time
from datetime import datetime

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

HISTORY_FILE = "history.json"
RISK_PERCENT = 0.02  # %2 risk

BIST30 = [
    "AKBNK.IS","ASELS.IS","BIMAS.IS","EREGL.IS",
    "FROTO.IS","GARAN.IS","KCHOL.IS","KOZAL.IS",
    "PETKM.IS","SAHOL.IS","SASA.IS","SISE.IS",
    "TCELL.IS","THYAO.IS","TUPRS.IS"
]

# ================================
# HISTORY
# ================================

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {
            "equity": 100000,
            "peak_equity": 100000,
            "trades": [],
            "wins": 0,
            "losses": 0
        }
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def save_history(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def update_drawdown(data):
    if data["equity"] > data["peak_equity"]:
        data["peak_equity"] = data["equity"]
    drawdown = (data["peak_equity"] - data["equity"]) / data["peak_equity"] * 100
    return round(drawdown,2)

# ================================
# TELEGRAM
# ================================

def send_telegram(message):
    if not TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": message})

# ================================
# ENGINE
# ================================

def process_trade(symbol, entry, stop, target, today):

    data = load_history()

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
    drawdown = update_drawdown(data)
    save_history(data)

    return trade, drawdown

# ================================
# STRATEGY
# ================================

def check_signal(symbol):

    df = yf.download(symbol, period="3mo", interval="1d", progress=False)
    if df.empty or len(df) < 60:
        return None

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    last = df.iloc[-2]
    today = df.iloc[-1]

    if last["EMA20"] > last["EMA50"]:

        entry = today["Open"]
        stop = entry * 0.97
        target = entry * 1.06

        return process_trade(symbol, entry, stop, target, today)

    return None

# ================================
# SCAN
# ================================

def run_scan():
    signals = []
    data = load_history()

    for symbol in BIST30:
        try:
            result = check_signal(symbol)
            if result:
                trade, drawdown = result
                signals.append(
                    f"{trade['symbol']} | {trade['result']} | "
                    f"PnL: {trade['pnl']} | DD: {drawdown}%"
                )
        except Exception as e:
            print("Error:", e)

    total = data["wins"] + data["losses"]
    winrate = (data["wins"]/total*100) if total>0 else 0
    drawdown = update_drawdown(data)

    message = "🏦 HEDGE FUND MOD 2.0\n\n"

    if signals:
        message += "\n".join(signals) + "\n\n"
    else:
        message += "Sinyal yok.\n\n"

    message += (
        f"💰 Equity: {round(data['equity'],2)}\n"
        f"📊 Winrate: {round(winrate,2)}%\n"
        f"📉 Drawdown: {drawdown}%\n"
        f"📈 Trades: {total}"
    )

    send_telegram(message)

# ================================
# ENDPOINTS
# ================================

@app.route("/")
def home():
    return "HEDGE FUND MOD 2.0 aktif."

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

# ================================
# AUTO SCHEDULER
# ================================

def auto_runner():
    while True:
        try:
            run_scan()
        except Exception as e:
            print("Auto error:", e)
        time.sleep(3600)

threading.Thread(target=auto_runner, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
