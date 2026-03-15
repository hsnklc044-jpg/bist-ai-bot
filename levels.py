import yfinance as yf

def calculate_support_resistance(symbol):

    ticker = yf.Ticker(symbol + ".IS")

    df = ticker.history(period="6mo")

    highs = df["High"]
    lows = df["Low"]

    resistance = highs.rolling(20).max().iloc[-1]
    support = lows.rolling(20).min().iloc[-1]

    return round(support,2), round(resistance,2)