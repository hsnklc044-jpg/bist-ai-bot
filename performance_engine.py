<<<<<<< HEAD
from journal_engine import get_journal


def analyze_performance():

    trades = get_journal()

    if not trades:
        return None

    total = len(trades)

    high_conf = 0
    total_conf = 0

    for t in trades:

        conf = t["confidence"]

        total_conf += conf

        if conf > 70:
            high_conf += 1

    win_rate = int((high_conf / total) * 100)

    avg_conf = int(total_conf / total)

    return {
        "trades": total,
        "win_rate": win_rate,
        "avg_conf": avg_conf
    }
=======
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
>>>>>>> b473b179fde9679eff721a025c85876a830c31be
