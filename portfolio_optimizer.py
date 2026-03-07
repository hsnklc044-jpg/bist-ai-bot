import numpy as np
from returns_engine import get_returns
from covariance_engine import covariance_matrix


def optimize_portfolio(symbols):

    returns = get_returns(symbols)

    cov = covariance_matrix(returns)

    mean_returns = returns.mean()

    num_assets = len(symbols)

    weights = np.ones(num_assets) / num_assets

    portfolio_return = np.dot(weights, mean_returns)

    portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))

    allocation = {}

    for i, symbol in enumerate(symbols):

        allocation[symbol] = round(weights[i] * 100,2)

    return {
        "return": round(portfolio_return * 100,2),
        "risk": round(portfolio_risk * 100,2),
        "allocation": allocation
    }
