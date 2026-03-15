import json
from optimizer_engine import optimize_rsi

FILE = "trades.json"


def get_adaptive_rsi():

    try:

        with open(FILE, "r") as f:
            trades = json.load(f)

    except:

        return optimize_rsi()

    if len(trades) < 10:

        return optimize_rsi()

    rsi_values = []

    for trade in trades:

        if "rsi" in trade:

            rsi_values.append(trade["rsi"])

    if not rsi_values:

        return optimize_rsi()

    avg_rsi = sum(rsi_values) / len(rsi_values)

    adaptive_rsi = avg_rsi - 2

    return round(adaptive_rsi, 2)
