import numpy as np
import pandas as pd
import yfinance as yf

RISK_FREE_RATE = 0.0
INITIAL_CAPITAL = 100000


# ================= DATA =================

def get_returns(symbols, period="3mo"):
    try:
        data = yf.download(symbols, period=period, auto_adjust=True)["Close"]
        if data is None or data.empty:
            return None
        returns = data.pct_change().dropna()
        return returns
    except:
        return None


# ================= AI VIEW (SAFE) =================

def build_ai_views():

    try:
        symbols = ["EREGL.IS", "SISE.IS", "KCHOL.IS"]

        P = np.eye(len(symbols))
        Q = np.array([0.05, 0.04, 0.06])  # AI beklenti (örnek)

        return P, Q, symbols

    except:
        return None, None, []


# ================= BLACK LITTERMAN =================

def black_litterman(returns, P, Q):

    cov = returns.cov()
    mu = returns.mean()

    tau = 0.05
    omega = np.diag(np.diag(P @ (tau * cov.values) @ P.T))

    middle = np.linalg.inv(
        np.linalg.inv(tau * cov.values) + P.T @ np.linalg.inv(omega) @ P
    )

    mu_bl = middle @ (
        np.linalg.inv(tau * cov.values) @ mu.values +
        P.T @ np.linalg.inv(omega) @ Q
    )

    return mu_bl, cov.values


# ================= OPTIMIZER =================

def optimize(mu, cov, returns):

    n = len(mu)

    inv_cov = np.linalg.pinv(cov)
    weights = inv_cov @ mu

    weights = weights / np.sum(np.abs(weights))

    weights = np.clip(weights, 0, 1)

    if np.sum(weights) == 0:
        weights = np.ones(n) / n
    else:
        weights = weights / np.sum(weights)

    return weights


# ================= FALLBACK =================

def fallback_portfolio():

    symbols = ["EREGL.IS", "SISE.IS", "KCHOL.IS"]

    weight = 1 / len(symbols)

    trades = []

    for s in symbols:
        trades.append({
            "symbol": s,
            "weight_%": round(weight * 100, 2),
            "allocation": round(weight * INITIAL_CAPITAL, 2),
            "lot": round((weight * INITIAL_CAPITAL) / 100, 0)
        })

    return {
        "portfolio": {
            "model": "Fallback Equal Weight",
            "expected_return_%": 8.0,
            "volatility_%": 15.0,
            "sharpe_ratio": 0.8,
            "leverage": 1.0
        },
        "trades": trades
    }


# ================= MAIN ENGINE =================

def scan_trades():

    try:
        P, Q, symbols = build_ai_views()

        if P is None or len(symbols) == 0:
            return fallback_portfolio()

        returns = get_returns(symbols)

        if returns is None or returns.empty:
            return fallback_portfolio()

        mu_bl, cov = black_litterman(returns, P, Q)
        weights = optimize(mu_bl, cov, returns)

        portfolio_return = float(np.sum(mu_bl * weights))
        portfolio_vol = float(np.sqrt(weights.T @ cov @ weights))

        sharpe = 0
        if portfolio_vol != 0:
            sharpe = (portfolio_return - RISK_FREE_RATE) / portfolio_vol

        trades = []

        for i, symbol in enumerate(symbols):
            if weights[i] > 0.02:
                trades.append({
                    "symbol": symbol,
                    "weight_%": round(weights[i] * 100, 2),
                    "allocation": round(weights[i] * INITIAL_CAPITAL, 2),
                    "lot": round((weights[i] * INITIAL_CAPITAL) / 100, 0)
                })

        if not trades:
            return fallback_portfolio()

        return {
            "portfolio": {
                "model": "Black-Litterman AI",
                "expected_return_%": round(portfolio_return * 100, 2),
                "volatility_%": round(portfolio_vol * 100, 2),
                "sharpe_ratio": round(sharpe, 2),
                "leverage": 1.0
            },
            "trades": trades
        }

    except Exception as e:
        print("ENGINE ERROR:", e)
        return fallback_portfolio()
