import json
import os

FILE = "signal_stats.json"


def load_stats():

    if not os.path.exists(FILE):
        return {}

    with open(FILE, "r") as f:
        return json.load(f)


def save_stats(stats):

    with open(FILE, "w") as f:
        json.dump(stats, f)


def update_stats(ticker, result):

    stats = load_stats()

    if ticker not in stats:

        stats[ticker] = {
            "wins": 0,
            "loss": 0
        }

    if result == "WIN":
        stats[ticker]["wins"] += 1

    if result == "LOSS":
        stats[ticker]["loss"] += 1

    save_stats(stats)


def get_rank_score(ticker):

    stats = load_stats()

    if ticker not in stats:
        return 0

    wins = stats[ticker]["wins"]
    loss = stats[ticker]["loss"]

    total = wins + loss

    if total == 0:
        return 0

    return round((wins / total) * 100, 2)
