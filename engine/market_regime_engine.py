import yfinance as yf


def market_regime():

    try:

        df = yf.download(
            "XU100.IS",
            period="6mo",
            interval="1d",
            progress=False
        )

        if df is None or df.empty:
            return "unknown"

        close = df["Close"]

        ma50 = close.rolling(50).mean()
        ma200 = close.rolling(200).mean()

        last_close = close.iloc[-1]
        last_ma50 = ma50.iloc[-1]
        last_ma200 = ma200.iloc[-1]

        if last_close > last_ma50 and last_ma50 > last_ma200:
            return "bull"

        if last_close < last_ma50 and last_ma50 < last_ma200:
            return "bear"

        return "sideways"

    except Exception as e:

        print("Market regime error:", e)

        return "unknown"
