import yfinance as yf


def get_trend(symbol):

    try:

        ticker = yf.Ticker(symbol + ".IS")

        data = ticker.history(period="5d", interval="5m")

        close = data["Close"]

        ema20 = close.ewm(span=20).mean().iloc[-1]

        ema50 = close.ewm(span=50).mean().iloc[-1]

        if ema20 > ema50:
            return "UP"

        else:
            return "DOWN"

    except:

        return None
