import yfinance as yf


def get_market_regime():

    try:

        data = yf.Ticker("XU100.IS").history(period="6mo")

        close = data["Close"]

        ma50 = close.tail(50).mean()
        ma200 = close.tail(200).mean()

        if ma50 > ma200:
            return "BULL"

        return "BEAR"

    except Exception as e:

        print("Market regime error:", e)

        return "UNKNOWN"
