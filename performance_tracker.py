import json
import os
import yfinance as yf
from datetime import datetime

TRACK_FILE = "signal_history.json"


def load_history():
    if not os.path.exists(TRACK_FILE):
        return []
    with open(TRACK_FILE, "r") as f:
        return json.load(f)


def save_history(data):
    with open(TRACK_FILE, "w") as f:
        json.dump(data, f)


def add_signal(symbol, entry, stop, target):
    history = load_history()

    history.append({
        "symbol": symbol,
        "entry": entry,
        "stop": stop,
        "target": target,
        "status": "OPEN",
        "date": datetime.now().strftime("%Y-%m-%d")
    })

    save_history(history)


def check_performance():
    history = load_history()
    updated = False

    for trade in history:
        if trade["status"] != "OPEN":
            continue

        df = yf.download(trade["symbol"], period="5d", interval="1d", progress=False)

        if df.empty:
            continue

        high = df["High"].max()
        low = df["Low"].min()

        if low <= trade["stop"]:
            trade["status"] = "STOP"
            updated = True

        elif high >= trade["target"]:
            trade["status"] = "TARGET"
            updated = True

    if updated:
        save_history(history)

    return history
