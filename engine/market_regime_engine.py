import yfinance as yf


def market_regime():

    try:

        symbol = "XU100.IS"

        df = yf.download(symbol, period="6mo", interval="1d", progress=False)

        if df is None or df.empty:
            return "UNKNOWN"

        close = df["Close"].astype(float)

        if len(close) < 50:
            return "UNKNOWN"

        ma20 = close.rolling(20).mean().iloc[-1]
        ma50 = close.rolling(50).mean().iloc[-1]

        price = close.iloc[-1]

        if price > ma20 and ma20 > ma50:
            return "BULL"

        if price < ma20 and ma20 < ma50:
            return "BEAR"

        return "SIDEWAYS"

    except Exception as e:

        print("Market regime error:", e)

        return "UNKNOWN"
