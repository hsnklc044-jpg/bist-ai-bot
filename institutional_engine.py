import yfinance as yf
import pandas as pd
import numpy as np
from scipy.optimize import minimize

ACCOUNT_SIZE = 100000
RISK_FREE_RATE = 0.25  # %25 varsayım
MIN_RR = 1.5

WATCHLIST = [
    "EREGL.IS","GARAN.IS","AKBNK.IS",
    "THYAO.IS","KCHOL.IS",
    "SISE.IS","BIMAS.IS",
    "ASELS.IS","TUPRS.IS","ISCTR.IS"
]

# ================= GET RETURNS =================
def get_returns(symbols):
    data = yf.download(symbols, period="6mo", interval="1d", progress=False)["Close"]
    returns = data.pct_change().dropna()
    return returns

# ================= MARKOWITZ =================
def optimize_portfolio(returns):

    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252
    num_assets = len(mean_returns)

    def negative_sharpe(weights):
        portfolio_return = np.sum(mean_returns * weights)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe = (portfolio_return - RISK_FREE_RATE) / portfolio_vol
        return -sharpe

    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0,1) for _ in range(num_assets))
    init_guess = num_assets * [1./num_assets]

    result = minimize(negative_sharpe,
                      init_guess,
                      method='SLSQP',
                      bounds=bounds,
                      constraints=constraints)

    return result.x

# ================= MAIN SCAN =================
def scan_trades():

    returns = get_returns(WATCHLIST)
    weights = optimize_portfolio(returns)

    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252

    portfolio_return = np.sum(mean_returns * weights)
    portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    sharpe = (portfolio_return - RISK_FREE_RATE) / portfolio_vol

    trades = []

    for i, symbol in enumerate(WATCHLIST):
        weight = weights[i]
        if weight < 0.05:
            continue

        allocation = ACCOUNT_SIZE * weight

        price = yf.download(symbol, period="5d", interval="1d", progress=False)["Close"].iloc[-1]
        lot = int(allocation / price)

        trades.append({
            "symbol": symbol.replace(".IS",""),
            "weight_%": round(weight*100,2),
            "allocation": round(allocation,2),
            "lot": lot
        })

    return {
        "portfolio": {
            "expected_return_%": round(portfolio_return*100,2),
            "volatility_%": round(portfolio_vol*100,2),
            "sharpe_ratio": round(sharpe,2)
        },
        "trades": trades
    }
