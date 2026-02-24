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

BIST30 = [
    "AKBNK.IS","ASELS.IS","BIMAS.IS","EREGL.IS",
    "FROTO.IS","GARAN.IS","KCHOL.IS","KOZAL.IS",
    "PETKM.IS","SAHOL.IS","SASA.IS","SISE.IS",
    "TCELL.IS","THYAO.IS","TUPRS.IS"
]

# ================================
# HISTORY & PERFORMANCE
# ================================

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {
            "equity": 100000,
            "trades": [],
            "wins": 0,
            "losses": 0
        }
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def save_history(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def record_trade(symbol, entry, exit_price):
    data = load_history()

    pnl = exit_price - entry
    data["equity"] += pnl

    trade = {
        "symbol": symbol,
        "entry": round(entry,2),
        "exit": round(exit_price,2),
        "pnl": round(pnl,2),
        "date": str(datetime.now())
    }

    data["trades"].append(trade)

    if pnl > 0:
        data["wins"] += 1
    else:
        data["losses"] += 1

    save_history(data)

def get_stats():
    data = load_history()
    total = data["wins"] + data["losses"]
    winrate = (data["wins"] / total * 100) if total > 0 else 0

    return {
        "equity": round(data["equity"],2),
        "wins": data["wins"],
        "losses": data["losses"],
        "winrate": round(winrate,2),
        "total_trades": total
    }

# ================================
# TELEGRAM
# ================================

def send_telegram(message):
    if not TOKEN or not CHAT_ID:
        print("Telegram bilgileri eksik.")
        return
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram hata:", e)

# ================================
# STRATEJİ ENGINE
# ================================

def check_signal(symbol):
    df = yf.download(symbol, period="3mo", interval="1d", progress=False)

    if df.empty or len(df) < 60:
        return None

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    last = df.iloc[-2]      # kapanmış mum
    today = df.iloc[-1]     # son mum

    if last["EMA20"] > last["EMA50"]:

        entry = today["Open"]
        tp = entry * 1.06
        sl = entry * 0.97

        # TP kontrol
        if today["High"] >= tp:
            record_trade(symbol, entry, tp)
            return f"{symbol} → WIN ✅"

        # SL kontrol
        elif today["Low"] <= sl:
            record_trade(symbol, entry, sl)
            return f"{symbol} → LOSS ❌"

    return None

# ================================
# SCAN
# ================================

def run_scan():
    print("Scan başladı:", datetime.now())

    signals = []

    for symbol in BIST30:
        try:
            result = check_signal(symbol)
            if result:
                signals.append(result)
        except Exception as e:
            print("Hata:", symbol, e)

    stats = get_stats()

    message = "🚀 ULTRA STABLE PRO BIST BOT\n\n"

    if signals:
        message += "\n".join(signals) + "\n\n"
    else:
        message += "Sinyal yok.\n\n"

    message += f"💰 Equity: {stats['equity']}\n"
    message += f"📊 Winrate: {stats['winrate']}%\n"
    message += f"📈 Trades: {stats['total_trades']}"

    send_telegram(message)

# ================================
# ENDPOINTS
# ================================

@app.route("/")
def home():
    return "ULTRA STABLE PRO BIST BOT aktif."

@app.route("/scan")
def manual_scan():
    run_scan()
    return "Scan tamamlandı."

@app.route("/equity")
def equity():
    stats = get_stats()
    return f"Equity: {stats['equity']} | Winrate: {stats['winrate']}% | Trades: {stats['total_trades']}"

# ================================
# OTOMATİK SCHEDULER
# ================================

def auto_runner():
    while True:
        try:
            run_scan()
        except Exception as e:
            print("Auto scan error:", e)
        time.sleep(3600)

threading.Thread(target=auto_runner, daemon=True).start()

# ================================
# RAILWAY START
# ================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
