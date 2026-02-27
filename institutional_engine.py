import yfinance as yf
import pandas as pd
import numpy as np
from scipy.optimize import minimize

# ================= SETTINGS =================
ACCOUNT_SIZE = 100000
RISK_FREE_RATE = 0.25
TAU = 0.05
LAMBDA = 2.0
TARGET_VOL = 0.20

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
    rs = avg_gain / (avg_loss + 1e-9)
    return 100 - (100 / (1 + rs))

# ================= ADAPTIVE AI =================
def build_ai_views():

    feature_matrix = []
    symbols_valid = []

    for symbol in WATCHLIST:
        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)
            if df.empty:
                continue

            close = df["Close"]
            volume = df["Volume"]

            rsi_series = rsi(close)
            momentum = close.pct_change(20)
            ema200 = close.ewm(span=200).mean()
            trend_dist = (close - ema200) / (ema200 + 1e-9)
            vol_ratio = volume / (volume.rolling(20).mean() + 1e-9)

            future_return = close.pct_change().shift(-5)

            data = pd.DataFrame({
                "rsi": rsi_series,
                "momentum": momentum,
                "trend": trend_dist,
                "volume": vol_ratio,
                "future": future_return
            }).dropna()

            if len(data) < 60:
                continue

            corr = data.corr()["future"].iloc[:-1].values

            feature_matrix.append(corr)
            symbols_valid.append(symbol)

        except:
            continue

    if len(feature_matrix) == 0:
        return None, None, None

    feature_matrix = np.array(feature_matrix)

    mean_corr = np.mean(feature_matrix, axis=0)
    mean_corr = np.maximum(mean_corr, 0)

    if np.sum(mean_corr) == 0:
        alpha_weights = np.ones(len(mean_corr)) / len(mean_corr)
    else:
        alpha_weights = mean_corr / np.sum(mean_corr)

    alpha_scores = feature_matrix @ alpha_weights

    P = np.eye(len(symbols_valid))
    Q = alpha_scores * 0.02

    return P, Q, symbols_valid

# ================= RETURNS =================
def get_returns(symbols):
    data = yf.download(symbols, period="6mo", interval="1d", progress=False)["Close"]
    returns = data.pct_change().dropna()
    return returns

# ================= BLACK LITTERMAN =================
def black_litterman(returns, P, Q):

    cov = returns.cov() * 252
    n = len(cov)

    market_weights = np.ones(n) / n
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

        if port_vol == 0:
            return 999

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
def monte_carlo_simulation(mu, cov, weights, days=60, simulations=500):

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
        "expected_%": round((np.mean(final_values)-1)*100,2),
        "worst_%": round((np.percentile(final_values,5)-1)*100,2),
        "best_%": round((np.percentile(final_values,95)-1)*100,2)
    }

# ================= KELLY =================
def kelly_position_size(portfolio_return, portfolio_vol):

    variance = portfolio_vol ** 2
    if variance == 0:
        return 0

    raw_kelly = (portfolio_return - RISK_FREE_RATE) / variance
    kelly_fraction = raw_kelly * 0.5
    kelly_fraction = max(0, min(kelly_fraction, 1.5))

    return round(kelly_fraction, 2)

# ================= VOL TARGET =================
def volatility_targeting(portfolio_vol):

    if portfolio_vol == 0:
        return 0

    scaling_factor = TARGET_VOL / portfolio_vol
    scaling_factor = min(max(scaling_factor, 0.5), 1.5)

    return round(scaling_factor, 2)

# ================= REGIME =================
def regime_multiplier():

    df = yf.download("XU100.IS", period="6mo", interval="1d", progress=False)
    if df.empty:
        return 1

    close = df["Close"]
    ema200 = close.ewm(span=200).mean()

    if close.iloc[-1] > ema200.iloc[-1]:
        return 1.0
    else:
        return 0.7

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

    sharpe = 0
    if portfolio_vol != 0:
        sharpe = (portfolio_return - RISK_FREE_RATE) / portfolio_vol

    monte_carlo = monte_carlo_simulation(mu_bl, cov, weights)
    kelly_fraction = kelly_position_size(portfolio_return, portfolio_vol)

    vol_scaler = volatility_targeting(portfolio_vol)
    regime_scale = regime_multiplier()

    final_leverage = round(min(kelly_fraction * vol_scaler * regime_scale, 1.5), 2)

    trades = []

    for i, symbol in enumerate(symbols):
        weight = weights[i]
        if weight < 0.05:
            continue

        price = yf.download(symbol, period="5d", interval="1d", progress=False)["Close"].iloc[-1]
        allocation = ACCOUNT_SIZE * weight * final_leverage
        lot = int(allocation / price)

        trades.append({
            "symbol": symbol.replace(".IS",""),
            "weight_%": round(weight*100,2),
            "allocation": round(allocation,2),
            "lot": lot
        })

    return {
        "portfolio": {
            "model": "Adaptive AI + BL + DD + MC + Kelly + VolTarget + Regime",
            "expected_return_%": round(portfolio_return*100,2),
            "volatility_%": round(portfolio_vol*100,2),
            "sharpe_ratio": round(sharpe,2),
            "kelly_fraction": kelly_fraction,
            "vol_scaler": vol_scaler,
            "regime_scale": regime_scale,
            "final_leverage": final_leverage
        },
        "monte_carlo_60d": monte_carlo,
        "trades": trades
    }
