import numpy as np


def calculate_position_size(portfolio_size, risk_percent, entry, stop):

    risk_amount = portfolio_size * (risk_percent / 100)

    stop_distance = abs(entry - stop)

    if stop_distance == 0:
        return 0

    position_size = risk_amount / stop_distance

    return int(position_size)


def volatility_adjustment(price_series):

    returns = price_series.pct_change().dropna()

    volatility = np.std(returns)

    if volatility > 0.04:
        return 0.5

    if volatility > 0.02:
        return 0.75

    return 1
