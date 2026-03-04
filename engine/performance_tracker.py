import json
import os

FILE = "performance_data.json"


def load_data():

    if not os.path.exists(FILE):
        return []

    with open(FILE, "r") as f:
        return json.load(f)


def save_data(data):

    with open(FILE, "w") as f:
        json.dump(data, f)


def record_signal(signal):

    data = load_data()

    data.append({
        "symbol": signal["symbol"],
        "entry": signal["entry"],
        "target": signal["target"],
        "stop": signal["stop"],
        "status": "OPEN"
    })

    save_data(data)


def calculate_performance():

    data = load_data()

    wins = 0
    losses = 0

    for s in data:

        if s["status"] == "WIN":
            wins += 1

        if s["status"] == "LOSS":
            losses += 1

    total = wins + losses

    if total == 0:
        return {
            "win_rate": 0,
            "signals": 0
        }

    win_rate = round((wins / total) * 100, 2)

    return {
        "win_rate": win_rate,
        "signals": total
    }
