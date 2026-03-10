import yfinance as yf


def get_market_regime():

    try:

        data = yf.download("XU100.IS", period="6mo", progress=False)

        ma50 = data["Close"].rolling(50).mean().iloc[-1]
        ma200 = data["Close"].rolling(200).mean().iloc[-1]

        price = data["Close"].iloc[-1]

        if price > ma50 and ma50 > ma200:
            return "BULLISH"

        if price < ma50 and ma50 < ma200:
            return "BEARISH"

        return "SIDEWAYS"

    except:

        return "UNKNOWN"
