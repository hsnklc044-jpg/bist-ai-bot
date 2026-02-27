import yfinance as yf
import pandas as pd
import numpy as np

BASE_RISK = 0.01
MIN_RR = 1.5   # Biraz esnettik
BREAKOUT_BUFFER = 0.97  # %3 tolerans

WATCHLIST = [
    "EREGL.IS","GARAN.IS","AKBNK.IS",
    "THYAO.IS","KCHOL.IS",
    "SISE.IS","BIMAS.IS",
    "ASELS.IS","TUPRS.IS","ISCTR.IS"
]

# ================= SAFE LAST VALUE =================
def last_value(data):
    """
    Series, DataFrame veya MultiIndex gelirse güvenli şekilde
    son değeri float olarak döndürür.
    """
    if isinstance(data, pd.DataFrame):
        data = data.iloc[:, 0]

    if isinstance(data, pd.Series):
        return float(data.iloc[-1])

    return float(data)

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
        return "NEUTRAL", 0.005, 2

    close = df["Close"]

    ema200 = close.ewm(span=200).mean()
    rsi_series = rsi(close)

    current_price = last_value(close)
    current_ema200 = last_value(ema200)
    current_rsi = last_value(rsi_series)

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

            close = df["Close"]
            high = df["High"]
            volume = df["Volume"]

            ema200 = close.ewm(span=200).mean()
            ema50 = close.ewm(span=50).mean()
            rsi_series = rsi(close)
            atr_series = atr(df)

            current_price = last_value(close)
            current_ema200 = last_value(ema200)
            current_ema50 = last_value(ema50)
            current_rsi = last_value(rsi_series)
            current_atr = last_value(atr_series)

            avg_volume = last_value(volume.rolling(20).mean())
            current_volume = last_value(volume)

            # Trend filtresi
            if current_price < current_ema200:
                continue

            # RSI filtresi (gevşek)
            if current_rsi < 45:
                continue

            # Hacim filtresi
            if current_volume < avg_volume * 1.1:
                continue

            # Breakout toleransı
            recent_high = float(high.tail(20).max())
            if current_price < recent_high * BREAKOUT_BUFFER:
                continue

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
                "symbol": symbol.replace(".IS",""),
                "price": round(current_price, 2),
                "breakout_entry": round(current_price, 2),
                "pullback_entry": round(current_ema50, 2),
                "stop": round(stop, 2),
                "target": round(target, 2),
                "rr": round(rr, 2),
                "score": round(rr, 2)
            })

        except Exception as e:
            print("SYMBOL ERROR:", symbol, e)
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
