import json
import os

TRADE_FILE = "trades.json"
WEIGHTS_FILE = "weights.json"


DEFAULT_WEIGHTS = {
    "market_regime_bull": 5,
    "market_regime_bear": -10,
    "whale_boost": 10,
    "sector_boost": 5,
    "momentum_boost": 8,
    "high_vol_penalty": -5,
    "low_vol_boost": 3
}


def get_weights():

    if not os.path.exists(WEIGHTS_FILE):
        save_weights(DEFAULT_WEIGHTS)
        return DEFAULT_WEIGHTS

    try:
        with open(WEIGHTS_FILE, "r") as f:
            return json.load(f)
    except:
        save_weights(DEFAULT_WEIGHTS)
        return DEFAULT_WEIGHTS


def save_weights(weights):

    with open(WEIGHTS_FILE, "w") as f:
        json.dump(weights, f, indent=4)


def optimize_weights():

    weights = get_weights()

    try:
        with open(TRADE_FILE, "r") as f:
            trades = json.load(f)
    except:
        return weights

    if len(trades) < 20:
        return weights

    profits = []
    last_prices = {}

    for trade in trades:

        symbol = trade["symbol"]
        price = trade["price"]

        if symbol in last_prices:

            old_price = last_prices[symbol]
            change = ((price - old_price) / old_price) * 100
            profits.append(change)

        last_prices[symbol] = price

    if not profits:
        return weights

    avg_profit = sum(profits) / len(profits)

    if avg_profit > 1:
        weights["momentum_boost"] += 1
        weights["whale_boost"] += 1

    elif avg_profit < 0:
        weights["high_vol_penalty"] -= 1
        weights["market_regime_bear"] -= 1

    # sınırlar
    weights["momentum_boost"] = min(max(weights["momentum_boost"], 3), 15)
    weights["whale_boost"] = min(max(weights["whale_boost"], 3), 20)
    weights["high_vol_penalty"] = min(max(weights["high_vol_penalty"], -15), -1)
    weights["market_regime_bear"] = min(max(weights["market_regime_bear"], -20), -3)

    save_weights(weights)

    return weights
