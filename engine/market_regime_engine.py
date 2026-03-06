import yfinance as yf


def get_market_regime():

    try:

        # BIST100 endeksi
        data = yf.download(
            "^XU100",
            period="3mo",
            interval="1d",
            progress=False
        )

        # veri gelmezse radar çalışmaya devam etsin
        if data is None or data.empty:
            print("⚠ XU100 verisi alınamadı, piyasa BULL varsayıldı")
            return "BULL"

        close = data["Close"]

        # yeterli veri yoksa radar çalışmaya devam etsin
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

        # hata olursa radar yine çalışsın
        return "BULL"
