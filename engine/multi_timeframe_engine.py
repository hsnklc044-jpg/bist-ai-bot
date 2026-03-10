import yfinance as yf


def multi_tf_trend(ticker):

    try:

        # 1H
        data1 = yf.Ticker(ticker).history(period="5d", interval="1h")

        # 4H
        data4 = yf.Ticker(ticker).history(period="1mo", interval="1h")

        # Daily
        dataD = yf.Ticker(ticker).history(period="6mo", interval="1d")

        if data1.empty or data4.empty or dataD.empty:
            return False

        close1 = data1["Close"]
        close4 = data4["Close"]
        closeD = dataD["Close"]

        ma20_1h = close1.tail(20).mean()
        ma50_1h = close1.tail(50).mean()

        ma20_4h = close4.tail(20).mean()
        ma50_4h = close4.tail(50).mean()

        ma50_d = closeD.tail(50).mean()
        ma200_d = closeD.tail(200).mean()

        if (
            ma20_1h > ma50_1h
            and ma20_4h > ma50_4h
            and ma50_d > ma200_d
        ):
            return True

        return False

    except Exception as e:

        print("Multi TF error:", ticker, e)

        return False
