import yfinance as yf


def calculate_risk(symbol):

    ticker = yf.Ticker(symbol + ".IS")

    df = ticker.history(period="6mo")

    close = df["Close"].iloc[-1]

    support = df["Low"].rolling(20).min().iloc[-1]

    resistance = df["High"].rolling(20).max().iloc[-1]

    entry = close
    stop = support
    target = resistance

    risk = entry - stop
    reward = target - entry

    rr = 0

    if risk > 0:
        rr = reward / risk

    confidence = "LOW"

    if rr > 2:
        confidence = "HIGH"
    elif rr > 1:
        confidence = "MEDIUM"

    return round(entry,2), round(stop,2), round(target,2), round(rr,2), confidence