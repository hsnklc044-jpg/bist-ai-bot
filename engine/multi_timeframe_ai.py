import yfinance as yf


def check_timeframe(symbol, interval):

    try:

        df = yf.download(
            symbol,
            period="1mo",
            interval=interval,
            progress=False
        )

        close = df["Close"]

        ema20 = close.ewm(span=20).mean().iloc[-1]
        ema50 = close.ewm(span=50).mean().iloc[-1]

        return ema20 > ema50

    except Exception as e:

        print("Timeframe error:", e)

        return False


def multi_timeframe_trend(symbol):

    ticker = f"{symbol}.IS"

    trend_1d = check_timeframe(ticker, "1d")
    trend_4h = check_timeframe(ticker, "1h")   # yfinance 4h yok, 1h kullanıyoruz
    trend_1h = check_timeframe(ticker, "30m")

    score = sum([trend_1d, trend_4h, trend_1h])

    return {
        "mtf_score": score,
        "strong_trend": score >= 2
    }
