import json
import os

FILE = "bot_performance.json"


def load_data():

    if not os.path.exists(FILE):
        return {
            "signals": 0,
            "wins": 0,
            "loss": 0
        }

    with open(FILE, "r") as f:
        return json.load(f)


def save_data(data):

    with open(FILE, "w") as f:
        json.dump(data, f)


def record_trade(result):

    data = load_data()

    data["signals"] += 1

    if result == "WIN":
        data["wins"] += 1

    if result == "LOSS":
        data["loss"] += 1

    save_data(data)


def get_stats():

    data = load_data()

    signals = data["signals"]
    wins = data["wins"]
    loss = data["loss"]

    if signals == 0:
        win_rate = 0
    else:
        win_rate = (wins / signals) * 100

    return {
        "signals": signals,
        "wins": wins,
        "loss": loss,
        "win_rate": round(win_rate,2)
    }
