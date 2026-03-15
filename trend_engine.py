import yfinance as yf


def get_trend(symbol):

    try:

        ticker = symbol + ".IS"

        df = yf.download(
            ticker,
            period="3mo",
            interval="1d",
            progress=False
        )

        if df is None or len(df) < 50:
            return "Veri yok"

        df["EMA20"] = df["Close"].ewm(span=20).mean()
        df["EMA50"] = df["Close"].ewm(span=50).mean()

        ema20 = df["EMA20"].iloc[-1]
        ema50 = df["EMA50"].iloc[-1]

        if ema20 > ema50:
            return "UPTREND"
        else:
            return "DOWNTREND"

    except:
        return "Trend hesaplanamadı"
