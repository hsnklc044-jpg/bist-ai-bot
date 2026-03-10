import yfinance as yf


def calculate_ai_score(symbol):

    try:

        ticker = f"{symbol}.IS"

        data = yf.download(ticker, period="3mo", interval="1d", progress=False)

        if data is None or data.empty:
            return None

        close = data["Close"]
        volume = data["Volume"]

        # son fiyat
        price = float(close.iloc[-1])

        # moving averages
        ma20 = close.rolling(20).mean().iloc[-1]
        ma50 = close.rolling(50).mean().iloc[-1]

        if ma20 is None or ma50 is None:
            return None

        ma20 = float(ma20)
        ma50 = float(ma50)

        score = 50

        # trend
        if price > ma20:
            score += 10

        if price > ma50:
            score += 10

        if ma20 > ma50:
            score += 10

        # momentum
        momentum_series = close.pct_change(10)
        momentum = momentum_series.iloc[-1]

        if momentum is not None and momentum > 0.05:
            score += 10

        # volume spike
        if volume.iloc[-1] > volume.mean():
            score += 10

        return score

    except Exception as e:

        print(symbol, "AI skor hatası:", e)
        return None
