import yfinance as yf


def get_market_regime():

    try:

        data = yf.download(
            "^XU100",
            period="3mo",
            interval="1d",
            progress=False
        )

        if data is None or data.empty:
            print("⚠ XU100 verisi alınamadı, piyasa BULL varsayıldı")
            return "BULL"

        close = data["Close"]

        if len(close) < 50:
            return "BULL"

        ma50 = close.rolling(50).mean().iloc[-1]
        last = close.iloc[-1]

        if last > ma50:

            print("📈 Piyasa yükseliş trendinde")

            return "BULL"

        else:

            print("📉 Piyasa düşüş trendinde")

            return "BEAR"

    except Exception as e:

        print("Market regime error:", e)

        return "BULL"
