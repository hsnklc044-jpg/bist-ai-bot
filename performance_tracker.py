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
        "rr": round((target - entry) / (entry - stop), 2),
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


def generate_statistics():
    history = load_history()

    total = len(history)
    wins = sum(1 for t in history if t["status"] == "TARGET")
    losses = sum(1 for t in history if t["status"] == "STOP")

    win_rate = round((wins / total) * 100, 2) if total > 0 else 0

    avg_rr = round(
        sum(t["rr"] for t in history if t["status"] == "TARGET") / wins,
        2
    ) if wins > 0 else 0

    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "avg_rr": avg_rr
    }
