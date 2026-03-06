import yfinance as yf


def get_market_sentiment():

    try:

        data = yf.download(
            "XU100.IS",
            period="3mo",
            interval="1d",
            progress=False
        )

        if data.empty:
            return "UNKNOWN"

        close = data["Close"]

        ma20 = close.rolling(20).mean().iloc[-1]
        ma50 = close.rolling(50).mean().iloc[-1]

        last_price = close.iloc[-1]

        if last_price > ma20 and ma20 > ma50:
            return "BULLISH"

        if last_price < ma20 and ma20 < ma50:
            return "BEARISH"

        return "NEUTRAL"

    except Exception as e:

        print("Sentiment error:", e)

        return "UNKNOWN"
