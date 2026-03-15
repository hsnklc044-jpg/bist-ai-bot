import json
from datetime import datetime

FILE = "trades.json"


def save_trade(symbol, price, rsi):

    trade = {
        "symbol": symbol,
        "price": price,
        "rsi": rsi,
        "time": str(datetime.now())
    }

    try:

        with open(FILE, "r") as f:
            data = json.load(f)

    except:
        data = []

    data.append(trade)

    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)
