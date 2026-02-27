import yfinance as yf
import pandas as pd
import numpy as np
from scipy.optimize import minimize

ACCOUNT_SIZE = 100000
RISK_FREE_RATE = 0.25
TAU = 0.05

WATCHLIST = [
    "EREGL.IS","GARAN.IS","AKBNK.IS",
    "THYAO.IS","KCHOL.IS",
    "SISE.IS","BIMAS.IS",
    "ASELS.IS","TUPRS.IS","ISCTR.IS"
]

# ================= RSI =================
def rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ================= GET RETURNS =================
def get_returns(symbols):
    data = yf.download(symbols, period="6mo", interval="1d", progress=False)["Close"]
    returns = data.pct_change().dropna()
    return returns

# ================= BUILD DYNAMIC VIEWS =================
def build_views(returns):

    views = []
    P = []

    index_data = yf.download("XU100.IS", period="6mo", interval="1d", progress=False)
    index_close = index_data["Close"]
    index_ema200 = index_close.ewm(span=200).mean()

    market_bear = index_close.iloc[-1] < index_ema200.iloc[-1]

    for i, symbol in enumerate(WATCHLIST):

        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        close = df["Close"]

        rsi_val = rsi(close).iloc[-1]
        momentum = close.iloc[-1] - close.iloc[-20]

        view_strength = 0

        # RSI View
        if rsi_val > 60:
            view_strength += 0.02
        elif rsi_val < 40:
            view_strength -= 0.02

        # Momentum View
        if momentum > 0:
            view_strength += 0.01
        else:
            view_strength -= 0.01

        # Macro View
        if market_bear:
            view_strength -= 0.02

        if abs(view_strength) > 0:
            row = np.zeros(len(WATCHLIST))
            row[i] = 1
            P.append(row)
            views.append(view_strength)

    if not P:
        return None, None

    P = np.array(P)
    Q = np.array(views)

    return P, Q

# ================= BLACK LITTERMAN =================
def black_litterman(returns):

    cov = returns.cov() * 252
    market_weights = np.ones(len(WATCHLIST)) / len(WATCHLIST)
    pi = cov @ market_weights

    P, Q = build_views(returns)

    if P is None:
        return pi, cov

    omega = np.diag(np.diag(P @ (TAU * cov) @ P.T))

    middle = np.linalg.inv(
        np.linalg.inv(TAU * cov) + P.T @ np.linalg.inv(omega) @ P
    )

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
            "model": "Dynamic Black-Litterman",
        },
        "trades": trades
    }
