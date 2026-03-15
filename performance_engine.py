import json

FILE = "trades.json"


def get_performance():

    try:
        with open(FILE, "r") as f:
            trades = json.load(f)
    except:
        return 0,0,0

    total = len(trades)

    if total == 0:
        return 0,0,0

    rsi_values = [t["rsi"] for t in trades]

    avg_rsi = round(sum(rsi_values)/len(rsi_values),2)

    return total, avg_rsi
