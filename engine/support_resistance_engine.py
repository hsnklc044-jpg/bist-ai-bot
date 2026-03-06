import yfinance as yf


def get_support_resistance(symbol):

    ticker = yf.download(symbol + ".IS", period="3mo", interval="1d")

    if ticker.empty:
        return None

    low = ticker["Low"]
    high = ticker["High"]
    close = ticker["Close"]

    support = round(low.tail(20).min(), 2)
    resistance = round(high.tail(20).max(), 2)

    price = round(close.iloc[-1], 2)

    return {

        "price": price,
        "support": support,
        "resistance": resistance

    }
