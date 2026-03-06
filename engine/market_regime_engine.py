import yfinance as yf


def get_market_regime():

    try:

        # BIST100 index
        symbol = "XU100.IS"

        df = yf.download(
            symbol,
            period="6mo",
            interval="1d",
            progress=False
        )

        if df is None or df.empty:
            return "UNKNOWN"

        close = df["Close"]

        if len(close) < 50:
            return "UNKNOWN"

        # moving averages
        ma20 = close.rolling(20).mean()
        ma50 = close.rolling(50).mean()

        price = float(close.iloc[-1])
        ma20_last = float(ma20.iloc[-1])
        ma50_last = float(ma50.iloc[-1])

        # BULL market
        if price > ma20_last and ma20_last > ma50_last:
            return "BULL"

        # BEAR market
        if price < ma20_last and ma20_last < ma50_last:
            return "BEAR"

        # otherwise sideways
        return "SIDEWAYS"

    except Exception as e:

        print("Market regime error:", e)

        return "UNKNOWN"
