import yfinance as yf


def market_summary():

    bist = yf.Ticker("XU100.IS")

    df = bist.history(period="3mo")

    close = df["Close"]

    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()

    trend = "Bearish"

    if ema20.iloc[-1] > ema50.iloc[-1]:
        trend = "Bullish"

    change = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100

    return trend, round(change,2)
