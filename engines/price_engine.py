import yfinance as yf


def get_price(symbol):

    ticker = yf.Ticker(symbol + ".IS")

    data = ticker.history(period="1d")

    if len(data) == 0:
        return 0

    price = round(data["Close"].iloc[-1],2)

    return price