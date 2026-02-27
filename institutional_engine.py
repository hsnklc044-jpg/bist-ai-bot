import yfinance as yf
import pandas as pd
import numpy as np
from scipy.optimize import minimize

ACCOUNT_SIZE = 100000
RISK_FREE_RATE = 0.25
TAU = 0.05  # View uncertainty

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

# ================= BLACK LITTERMAN =================
def black_litterman(returns):

    cov = returns.cov() * 252
    market_weights = np.ones(len(WATCHLIST)) / len(WATCHLIST)

    # Implied equilibrium returns
    pi = cov @ market_weights

    # === VIEW EXAMPLE ===
    # "THYAO piyasadan %3 daha iyi performans gösterecek"
    P = np.zeros((1, len(WATCHLIST)))
    Q = np.array([0.03])

    idx = WATCHLIST.index("THYAO.IS")
    P[0, idx] = 1

    omega = np.diag(np.diag(P @ (TAU * cov) @ P.T))

    middle = np.linalg.inv(np.linalg.inv(TAU * cov) + P.T @ np.linalg.inv(omega) @ P)
    mu_bl = middle @ (
        np.linalg.inv(TAU * cov) @ pi +
        P.T @ np.linalg.inv(omega) @ Q
    )

    return mu_bl, cov

# ================= OPTIMIZER =================
def optimize(mu, cov):

    def negative_sharpe(weights):
        port_return = np.sum(mu * weights)
        port_vol = np.sqrt(weights.T @ cov @ weights)
        return -(port_return - RISK_FREE_RATE) / port_vol

    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0,1) for _ in range(len(mu)))
    init_guess = np.ones(len(mu)) / len(mu)

    result = minimize(negative_sharpe,
                      init_guess,
                      method='SLSQP',
                      bounds=bounds,
                      constraints=constraints)

    return result.x

# ================= MAIN =================
def scan_trades():

    returns = get_returns(WATCHLIST)
    mu_bl, cov = black_litterman(returns)

    weights = optimize(mu_bl, cov)

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
            "model": "Black-Litterman",
        },
        "trades": trades
    }
