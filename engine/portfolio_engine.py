import json
import os

PORTFOLIO_FILE = "portfolio.json"


def load_portfolio():

    if not os.path.exists(PORTFOLIO_FILE):
        return []

    try:
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_portfolio(data):

    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(data, f, indent=4)


def is_symbol_active(symbol):

    portfolio = load_portfolio()

    for trade in portfolio:
        if trade["symbol"] == symbol:
            return True

    return False


def add_trade(symbol, entry, stop, target):

    portfolio = load_portfolio()

    portfolio.append({
        "symbol": symbol,
        "entry": entry,
        "stop": stop,
        "target": target
    })

    save_portfolio(portfolio)
