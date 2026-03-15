import yfinance as yf

def ai_trade(symbol):

    ticker = yf.Ticker(symbol + ".IS")

    df = ticker.history(period="6mo")

    close = df["Close"].iloc[-1]

    support = df["Low"].rolling(20).min().iloc[-1]
    resistance = df["High"].rolling(20).max().iloc[-1]

    target = resistance
    entry = close

    confidence = "MEDIUM"

    if entry > df["Close"].ewm(span=20).mean().iloc[-1]:
        confidence = "HIGH"

    return round(entry,2), round(support,2), round(target,2), confidence