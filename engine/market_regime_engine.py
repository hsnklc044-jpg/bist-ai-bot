import yfinance as yf


def market_regime():

    try:

        data = yf.download("^XU100", period="6mo")

        if data.empty:
            return "UNKNOWN"

        close = data["Close"]

        if hasattr(close, "columns"):
            close = close.iloc[:, 0]

        ma50 = close.rolling(50).mean().iloc[-1]
        price = close.iloc[-1]

        if price > ma50:
            return "BULL"

        return "BEAR"

    except Exception as e:

        print("Market regime error:", e)

        return "UNKNOWN"
