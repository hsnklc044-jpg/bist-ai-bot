import yfinance as yf
import pandas as pd
import numpy as np
from scipy.optimize import minimize

ACCOUNT_SIZE = 100000
RISK_FREE_RATE = 0.25
TAU = 0.05
LAMBDA = 2.0

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

# ================= FEATURES =================
def compute_features(symbol):
    df = yf.download(symbol, period="6mo", interval="1d", progress=False)
    if df.empty:
        return None

    close = df["Close"]
    volume = df["Volume"]

    rsi_val = rsi(close).iloc[-1]
    momentum = close.iloc[-1] / close.iloc[-20] - 1
    ema200 = close.ewm(span=200).mean().iloc[-1]
    trend_dist = (close.iloc[-1] - ema200) / ema200
    vol_ratio = volume.iloc[-1] / volume.rolling(20).mean().iloc[-1]

    return np.array([rsi_val, momentum, trend_dist, vol_ratio])

# ================= AI VIEW =================
def build_ai_views():
    feature_matrix = []
    symbols_valid = []

    for symbol in WATCHLIST:
        features = compute_features(symbol)
        if features is not None:
            feature_matrix.append(features)
            symbols_valid.append(symbol)

    if not feature_matrix:
        return None, None, None

    feature_matrix = np.array(feature_matrix)
    feature_matrix = (feature_matrix - feature_matrix.mean(axis=0)) / feature_matrix.std(axis=0)

    alpha_weights = np.array([0.3, 0.3, 0.2, 0.2])
    alpha_scores = feature_matrix @ alpha_weights

    P = np.zeros((len(symbols_valid), len(symbols_valid)))
    Q = []

    for i in range(len(symbols_valid)):
        P[i, i] = 1
        Q.append(alpha_scores[i] * 0.02)

    return np.array(P), np.array(Q), symbols_valid

# ================= RETURNS =================
def get_returns(symbols):
    data = yf.download(symbols, period="6mo", interval="1d", progress=False)["Close"]
    return data.pct_change().dropna()

# ================= BLACK LITTERMAN =================
def black_litterman(returns, P, Q):
    cov = returns.cov() * 252
    market_weights = np.ones(len(returns.columns)) / len(returns.columns)
    pi = cov @ market_weights

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
def optimize(mu, cov, returns):

    def objective(weights):
        port_returns = returns @ weights
        equity = (1 + port_returns).cumprod()
        peak = equity.cummax()
        drawdown = (equity - peak) / peak
        max_dd = abs(drawdown.min())

        port_return = np.sum(mu * weights)
        port_vol = np.sqrt(weights.T @ cov @ weights)
        sharpe = (port_return - RISK_FREE_RATE) / port_vol

        return -(sharpe - LAMBDA * max_dd)

    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0,1) for _ in range(len(mu)))
    init_guess = np.ones(len(mu)) / len(mu)

    result = minimize(objective,
                      init_guess,
                      method='SLSQP',
                      bounds=bounds,
                      constraints=constraints)

    return result.x

# ================= MONTE CARLO =================
def monte_carlo_simulation(mu, cov, weights, days=60, simulations=1000):

    port_mean = np.sum(mu * weights) / 252
    port_vol = np.sqrt(weights.T @ cov @ weights) / np.sqrt(252)

    final_values = []

    for _ in range(simulations):
        daily_returns = np.random.normal(port_mean, port_vol, days)
        equity = 1
        for r in daily_returns:
            equity *= (1 + r)
        final_values.append(equity)

    return {
        "expected_return_%": round((np.mean(final_values)-1)*100,2),
        "worst_case_%": round((np.percentile(final_values,5)-1)*100,2),
        "best_case_%": round((np.percentile(final_values,95)-1)*100,2)
    }

# ================= MAIN =================
def scan_trades():

    P, Q, symbols = build_ai_views()
    if P is None:
        return {"error": "Feature üretilemedi"}

    returns = get_returns(symbols)
    mu_bl, cov = black_litterman(returns, P, Q)
    weights = optimize(mu_bl, cov, returns)

    portfolio_return = np.sum(mu_bl * weights)
    portfolio_vol = np.sqrt(weights.T @ cov @ weights)
    sharpe = (portfolio_return - RISK_FREE_RATE) / portfolio_vol

    monte_carlo = monte_carlo_simulation(mu_bl, cov, weights)

    trades = []

    for i, symbol in enumerate(symbols):
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
            "model": "AI BL + Drawdown + MonteCarlo",
            "expected_return_%": round(portfolio_return*100,2),
            "volatility_%": round(portfolio_vol*100,2),
            "sharpe_ratio": round(sharpe,2)
        },
        "monte_carlo_60d": monte_carlo,
        "trades": trades
    }
