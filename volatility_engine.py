import yfinance as yf
import pandas as pd


def volatility_analysis(symbol):

    ticker = yf.Ticker(symbol + ".IS")

    df = ticker.history(period="6mo")

    if df.empty:
        return 0, "UNKNOWN", 0, "UNKNOWN"

    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(14).mean().iloc[-1]

    volatility = "LOW"

    if atr > close.iloc[-1] * 0.03:
        volatility = "HIGH"
    elif atr > close.iloc[-1] * 0.015:
        volatility = "MEDIUM"

    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()

    trend_strength = abs(ema20.iloc[-1] - ema50.iloc[-1])

    risk = "LOW"

    if volatility == "HIGH":
        risk = "HIGH"
    elif volatility == "MEDIUM":
        risk = "MEDIUM"

    return round(atr,2), volatility, round(trend_strength,2), risk