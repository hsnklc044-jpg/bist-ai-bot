import yfinance as yf
import pandas as pd
import numpy as np

# ================= SETTINGS =================
ACCOUNT_SIZE = 100000
BASE_RISK = 0.01
MIN_RR = 1.5
BREAKOUT_BUFFER = 0.97
MAX_CORRELATION = 0.80

WATCHLIST = [
    "EREGL.IS","GARAN.IS","AKBNK.IS",
    "THYAO.IS","KCHOL.IS",
    "SISE.IS","BIMAS.IS",
    "ASELS.IS","TUPRS.IS","ISCTR.IS"
]

# ================= HELPERS =================
def last(series):
    if isinstance(series, pd.DataFrame):
        series = series.iloc[:, 0]
    return float(series.iloc[-1])

def rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def atr(df, period=14):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(period).mean()

# ================= MARKET REGIME =================
def market_regime():

    df = yf.download("XU100.IS", period="6mo", interval="1d", progress=False)
    if df.empty:
        return "NEUTRAL", BASE_RISK

    close = df["Close"]
    ema200 = close.ewm(span=200).mean()
    rsi_series = rsi(close)

    price = last(close)
    ema = last(ema200)
    rsi_val = last(rsi_series)

    if price > ema and rsi_val > 50:
        return "BULL", BASE_RISK
    elif price > ema:
        return "NEUTRAL", BASE_RISK * 0.5
    else:
        return "BEAR", 0

# ================= CORRELATION =================
def is_correlated(new_symbol, selected_symbols):
    if not selected_symbols:
        return False

    symbols = selected_symbols + [new_symbol]
    data = yf.download(symbols, period="60d", interval="1d", progress=False)["Close"]
    returns = data.pct_change().dropna()
    corr = returns.corr()

    for s in selected_symbols:
        if corr.loc[new_symbol, s] > MAX_CORRELATION:
            return True
    return False

# ================= BETA =================
def calculate_beta(symbol):
    try:
        data = yf.download([symbol,"XU100.IS"], period="6mo", interval="1d", progress=False)["Close"]
        returns = data.pct_change().dropna()
        stock = returns[symbol]
        index = returns["XU100.IS"]
        cov = np.cov(stock, index)[0][1]
        var = np.var(index)
        return round(cov/var,2)
    except:
        return 1.0

# ================= MAIN SCAN =================
def scan_trades():

    regime, risk_per_trade = market_regime()

    trades = []
    betas = []
    portfolio_value = 0
    selected_symbols = []

    if regime == "BEAR":
        return {
            "regime": {
                "regime": regime,
                "risk_%": 0,
                "portfolio_beta": 0,
                "hedge_ratio": 1.0,
                "hedge_lot_xu100": "FULL HEDGE"
            },
            "trades": []
        }

    for symbol in WATCHLIST:

        if is_correlated(symbol, selected_symbols):
            continue

        try:
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)
            if df.empty:
                continue

            close = df["Close"]
            high = df["High"]
            volume = df["Volume"]

            ema200 = close.ewm(span=200).mean()
            rsi_series = rsi(close)
            atr_series = atr(df)

            price = last(close)
            ema = last(ema200)
            rsi_val = last(rsi_series)
            atr_val = last(atr_series)

            avg_vol = last(volume.rolling(20).mean())
            cur_vol = last(volume)

            if price < ema or rsi_val < 50 or cur_vol < avg_vol:
                continue

            recent_high = float(high.tail(20).max())
            if price < recent_high * BREAKOUT_BUFFER:
                continue

            stop = price - atr_val * 1.5
            target = price + atr_val * 3

            risk = price - stop
            reward = target - price
            if risk <= 0:
                continue

            rr = reward / risk
            if rr < MIN_RR:
                continue

            risk_amount = ACCOUNT_SIZE * risk_per_trade
            qty = int(risk_amount / risk)
            position_value = qty * price

            portfolio_value += position_value
            selected_symbols.append(symbol)

            beta = calculate_beta(symbol)
            betas.append(beta)

            trades.append({
                "symbol": symbol.replace(".IS",""),
                "entry": round(price,2),
                "stop": round(stop,2),
                "target": round(target,2),
                "rr": round(rr,2),
                "lot": qty,
                "beta": beta
            })

        except:
            continue

    portfolio_beta = round(np.mean(betas),2) if betas else 0
    hedge_ratio = max(portfolio_beta - 1, 0)

    index_df = yf.download("XU100.IS", period="5d", interval="1d", progress=False)
    index_price = last(index_df["Close"]) if not index_df.empty else 0

    hedge_value = portfolio_value * hedge_ratio
    hedge_lot = int(hedge_value / index_price) if index_price > 0 else 0

    return {
        "regime": {
            "regime": regime,
            "risk_%": round(risk_per_trade*100,2),
            "portfolio_beta": portfolio_beta,
            "hedge_ratio": round(hedge_ratio,2),
            "hedge_lot_xu100": hedge_lot
        },
        "trades": trades
    }
