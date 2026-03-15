import json

TRADE_FILE = "trades.json"


def calculate_profit():

    try:
        with open(TRADE_FILE, "r") as f:
            trades = json.load(f)
    except:
        return 0,0,0

    if len(trades) < 2:
        return 0,0,0

    profits = []

    last_price = {}

    for trade in trades:

        symbol = trade["symbol"]
        price = trade["price"]

        if symbol in last_price:

            entry = last_price[symbol]

            change = ((price - entry) / entry) * 100

            profits.append(change)

        last_price[symbol] = price

    if not profits:
        return 0,0,0

    avg_profit = round(sum(profits)/len(profits),2)

    wins = [p for p in profits if p > 0]

    win_rate = round((len(wins)/len(profits))*100,2)

    total = len(profits)

    return avg_profit, win_rate, total
