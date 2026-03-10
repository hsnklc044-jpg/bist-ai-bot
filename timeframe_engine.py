import yfinance as yf


def timeframe_trend(symbol):

    try:

        daily = yf.download(symbol, period="3mo", interval="1d", progress=False)
        weekly = yf.download(symbol, period="1y", interval="1wk", progress=False)

        daily_ma = daily["Close"].rolling(20).mean().iloc[-1]
        weekly_ma = weekly["Close"].rolling(20).mean().iloc[-1]

        price = daily["Close"].iloc[-1]

        daily_trend = price > daily_ma
        weekly_trend = price > weekly_ma

        if daily_trend and weekly_trend:
            return "STRONG_UP"

        if daily_trend:
            return "UP"

        return "DOWN"

    except:

        return "UNKNOWN"
