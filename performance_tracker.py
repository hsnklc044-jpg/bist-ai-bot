import json
import os

FILE = "performance.json"


def load_performance():

    if not os.path.exists(FILE):
        return {}

    with open(FILE, "r") as f:
        return json.load(f)


def save_performance(data):

    with open(FILE, "w") as f:
        json.dump(data, f)


def update_performance(ticker, win_rate):

    data = load_performance()

    data[ticker] = win_rate

    save_performance(data)


def get_performance(ticker):

    data = load_performance()

    if ticker not in data:
        return 0

    return data[ticker]
