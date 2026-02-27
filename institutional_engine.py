import yfinance as yf
import pandas as pd
import numpy as np

BASE_RISK = 0.01
MIN_RR = 2.0

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


# ================= ATR =================
def atr(df, period=14):

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    high = pd.Series(df["High"]).astype(float)
    low = pd.Series(df["Low"]).astype(float)
    close = pd.Series(df["Close"]).astype(float)

    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(period).mean()


# ================= MARKET REGIME =================
def market_regime():

    df = yf.download("XU100.IS", period="6mo", interval="1d", progress=False)

    if df.empty:
        return "NEUTRAL", 0.005, 2

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    close = pd.Series(df["Close"]).astype(float)

    ema200 = close.ewm(span=200).mean()
    rsi_series = rsi(close)

    if len(close) < 200:
        return "NEUTRAL", 0.005, 2

    current_price = float(close.values[-1])
    current_ema200 = float(ema200.values[-1])
    current_rsi = float(rsi_series.values[-1])

    if current_price > current_ema200 and current_rsi > 50:
        return "BULL", 0.01, 3
    elif current_price > current_ema200:
        return "NEUTRAL", 0.005, 2
    else:
        return "BEAR", 0.0, 0


# ================= SCAN =================
def scan_trades():

    regime, risk_per_trade, max_trades = market_regime()

    if regime == "BEAR":
        return {
            "regime": {
                "regime": regime,
                "risk": risk_per_trade,
                "max_trades": max_trades
            },
            "trades": []
        }

    trades = []

    for symbol in WATCHLIST:

        try:
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)

            if df.empty:
                continue

            # MultiIndex güvenliği
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            close = pd.Series(df["Close"]).astype(float)
            high = pd.Series(df["High"]).astype(float)

            if len(close) < 200:
                continue

            ema200 = close.ewm(span=200).mean()
            rsi_series = rsi(close)
            atr_series = atr(df)

            current_price = float(close.values[-1])
            current_ema200 = float(ema200.values[-1])
            current_rsi = float(rsi_series.values[-1])
            current_atr = float(atr_series.values[-1])

            # Trend filtresi
            if current_price < current_ema200:
                continue

            # RSI filtresi
            if current_rsi < 48:
                continue

            # 20 günlük tepe
            recent_high = float(high.tail(20).max())

            if current_price < recent_high * 0.99:
                continue

            # Risk hesaplama
            stop = current_price - (current_atr * 1.5)
            target = current_price + (current_atr * 3)

            risk = current_price - stop
            reward = target - current_price

            if risk <= 0:
                continue

            rr = reward / risk

            if rr < MIN_RR:
                continue

            trades.append({
                "symbol": symbol,
                "price": round(current_price, 2),
                "breakout_entry": round(current_price, 2),
                "pullback_entry": round(current_price * 0.98, 2),
                "stop": round(stop, 2),
                "target": round(target, 2),
                "rr": round(rr, 2),
                "score": round(rr, 2)
            })

        except Exception as e:
            print("SCAN ERROR:", e)
            continue

    trades = sorted(trades, key=lambda x: x["score"], reverse=True)

    return {
        "regime": {
            "regime": regime,
            "risk": risk_per_trade,
            "max_trades": max_trades
        },
        "trades": trades[:max_trades]
    }
