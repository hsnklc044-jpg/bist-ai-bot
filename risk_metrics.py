import numpy as np


def calculate_risk_metrics(returns):

    if len(returns) == 0:
        return {
            "sharpe": 0,
            "max_drawdown": 0
        }

    returns = np.array(returns)

    sharpe = np.mean(returns) / np.std(returns)

    cumulative = np.cumsum(returns)

    peak = np.maximum.accumulate(cumulative)

    drawdown = cumulative - peak

    max_drawdown = drawdown.min()

    return {
        "sharpe": round(sharpe,2),
        "max_drawdown": round(max_drawdown,2)
    }
