import json
import os

FILE = "strategy_stats.json"


def load_stats():

    if not os.path.exists(FILE):
        return {}

    with open(FILE, "r") as f:
        return json.load(f)


def save_stats(stats):

    with open(FILE, "w") as f:
        json.dump(stats, f)


def update_strategy(name, result):

    stats = load_stats()

    if name not in stats:

        stats[name] = {
            "wins": 0,
            "loss": 0
        }

    if result == "WIN":
        stats[name]["wins"] += 1

    if result == "LOSS":
        stats[name]["loss"] += 1

    save_stats(stats)
