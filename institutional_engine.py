import numpy as np
import pandas as pd
import yfinance as yf

RISK_FREE_RATE = 0.0
INITIAL_CAPITAL = 100000
RISK_PER_TRADE_PCT = 0.01


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


# ================= ATR =================

def get_atr(symbol, period="3mo", window=14):
    try:
        df = yf.download(symbol, period=period, auto_adjust=True)

        if df is None or df.empty:
            return None

        high = df["High"]
        low = df["Low"]
        close = df["Close"]

        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=window).mean()

        return float(atr.iloc[-1])

    except:
        return None


# ================= REGIME DETECTION =================

def detect_regime():

    try:
        bist = yf.download("XU100.IS", period="3mo", auto_adjust=True)["Close"]

        returns = bist.pct_change().dropna()
        vol = returns.rolling(20).std().iloc[-1] * np.sqrt(252)

        if vol < 0.15:
            return "RISK_ON", 1.2
        elif vol < 0.25:
            return "NORMAL", 1.0
        elif vol < 0.35:
            return "RISK_OFF", 0.7
        else:
            return "PANIC", 0.4

    except:
        return "NORMAL", 1.0


# ================= AI VIEW =================

def build_ai_views():
    try:
        symbols = ["EREGL.IS", "SISE.IS", "KCHOL.IS"]
        P = np.eye(len(symbols))
        Q = np.array([0.05, 0.04, 0.06])
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

def optimize(mu, cov):

    inv_cov = np.linalg.pinv(cov)
    weights = inv_cov @ mu

    weights = weights / np.sum(np.abs(weights))
    weights = np.clip(weights, 0, 1)

    if np.sum(weights) == 0:
        weights = np.ones(len(mu)) / len(mu)
    else:
        weights = weights / np.sum(weights)

    return weights


# ================= FALLBACK =================

def fallback_portfolio():

    symbols = ["EREGL.IS", "SISE.IS", "KCHOL.IS"]
    weight = 1 / len(symbols)

    regime, leverage = detect_regime()

    trades = []
    equity = INITIAL_CAPITAL * leverage
    risk_per_trade = equity * RISK_PER_TRADE_PCT

    for s in symbols:

        atr = get_atr(s)
        if atr is None or atr == 0:
            continue

        stop_distance = atr * 1.5
        lot = risk_per_trade / stop_distance

        trades.append({
            "symbol": s,
            "weight_%": round(weight * 100, 2),
            "allocation": round(weight * equity, 2),
            "lot": round(lot, 0),
            "stop_distance": round(stop_distance, 2)
        })

    return {
        "portfolio": {
            "model": f"Fallback Equal Weight ({regime})",
            "expected_return_%": 8.0,
            "volatility_%": 15.0,
            "sharpe_ratio": 0.8,
            "leverage": leverage
        },
        "trades": trades
    }


# ================= MAIN ENGINE =================

def scan_trades():

    try:
        regime, leverage = detect_regime()

        P, Q, symbols = build_ai_views()
        if P is None or len(symbols) == 0:
            return fallback_portfolio()

        returns = get_returns(symbols)
        if returns is None or returns.empty:
            return fallback_portfolio()

        mu_bl, cov = black_litterman(returns, P, Q)
        weights = optimize(mu_bl, cov)

        portfolio_return = float(np.sum(mu_bl * weights))
        portfolio_vol = float(np.sqrt(weights.T @ cov @ weights))

        sharpe = 0
        if portfolio_vol != 0:
            sharpe = (portfolio_return - RISK_FREE_RATE) / portfolio_vol

        trades = []

        equity = INITIAL_CAPITAL * leverage
        risk_per_trade = equity * RISK_PER_TRADE_PCT

        for i, symbol in enumerate(symbols):

            if weights[i] > 0.02:

                atr = get_atr(symbol)
                if atr is None or atr == 0:
                    continue

                stop_distance = atr * 1.5
                lot = risk_per_trade / stop_distance

                trades.append({
                    "symbol": symbol,
                    "weight_%": round(weights[i] * 100, 2),
                    "allocation": round(weights[i] * equity, 2),
                    "lot": round(lot, 0),
                    "stop_distance": round(stop_distance, 2)
                })

        if not trades:
            return fallback_portfolio()

        return {
            "portfolio": {
                "model": f"Black-Litterman AI (ATR + Regime: {regime})",
                "expected_return_%": round(portfolio_return * 100, 2),
                "volatility_%": round(portfolio_vol * 100, 2),
                "sharpe_ratio": round(sharpe, 2),
                "leverage": leverage
            },
            "trades": trades
        }

    except Exception as e:
        print("ENGINE ERROR:", e)
        return fallback_portfolio()
