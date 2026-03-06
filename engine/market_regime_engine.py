import yfinance as yf

def get_market_regime():

    try:

        data = yf.download("^XU100", period="3mo", interval="1d")

        if data is None or data.empty:
            return "BULL"

        close = data["Close"]

        ma50 = close.rolling(50).mean().iloc[-1]

        last = close.iloc[-1]

        if last > ma50:
            return "BULL"
        else:
            return "BEAR"

    except:

        return "BULL"
