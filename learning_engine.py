import json
import os

FILE = "learning_data.json"


def load_data():

    if not os.path.exists(FILE):
        return {}

    with open(FILE, "r") as f:
        return json.load(f)


def save_data(data):

    with open(FILE, "w") as f:
        json.dump(data, f)


def record_signal(ticker, score):

    data = load_data()

    if ticker not in data:

        data[ticker] = {
            "count": 0,
            "avg_score": 0
        }

    entry = data[ticker]

    entry["count"] += 1

    entry["avg_score"] = ((entry["avg_score"] * (entry["count"] - 1)) + score) / entry["count"]

    data[ticker] = entry

    save_data(data)


def learning_bonus(ticker):

    data = load_data()

    if ticker not in data:
        return 0

    avg = data[ticker]["avg_score"]

    if avg > 80:
        return 10

    if avg > 70:
        return 5

    return 0
