import yfinance as yf


def get_market_sentiment():

    try:

        bist = yf.download("^XU100", period="3mo", progress=False)
        sp500 = yf.download("^GSPC", period="3mo", progress=False)

        if bist.empty or sp500.empty:
            return "NEUTRAL"

        bist_close = bist["Close"]
        sp_close = sp500["Close"]

        if hasattr(bist_close, "columns"):
            bist_close = bist_close.iloc[:,0]

        if hasattr(sp_close, "columns"):
            sp_close = sp_close.iloc[:,0]

        bist_ma = bist_close.rolling(50).mean().iloc[-1]
        sp_ma = sp_close.rolling(50).mean().iloc[-1]

        bist_price = bist_close.iloc[-1]
        sp_price = sp_close.iloc[-1]

        if bist_price > bist_ma and sp_price > sp_ma:
            return "BULL"

        if bist_price < bist_ma and sp_price < sp_ma:
            return "BEAR"

        return "NEUTRAL"

    except Exception as e:

        print("Sentiment error:", e)

        return "NEUTRAL"
