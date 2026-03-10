import yfinance as yf


def get_market_status():

    ticker = yf.Ticker("XU100.IS")

    df = ticker.history(period="6mo")

    if df.empty:
        return None

    price = float(df["Close"].iloc[-1])

    ma20 = float(df["Close"].tail(20).mean())
    ma50 = float(df["Close"].tail(50).mean())

    momentum = float(df["Close"].iloc[-1]) - float(df["Close"].iloc[-5])

    # trend
    if price > ma20 and ma20 > ma50:
        trend = "Bullish"

    elif price < ma20 and ma20 < ma50:
        trend = "Bearish"

    else:
        trend = "Sideways"

    # momentum
    if momentum > 0:
        momentum_status = "Strong"
    else:
        momentum_status = "Weak"

    # risk
    if trend == "Bullish" and momentum_status == "Strong":
        risk = "Low"

    elif trend == "Bearish":
        risk = "High"

    else:
        risk = "Medium"

    return {
        "trend": trend,
        "momentum": momentum_status,
        "risk": risk
    }