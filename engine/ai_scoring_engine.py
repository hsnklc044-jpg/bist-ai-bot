import yfinance as yf


def calculate_ai_score(symbol):

    try:

        ticker = f"{symbol}.IS"

        data = yf.download(ticker, period="3mo", interval="1d")

        if data.empty:
            return None

        close = data["Close"]
        volume = data["Volume"]

        price = float(close.iloc[-1])

        ma20 = float(close.rolling(20).mean().iloc[-1])
        ma50 = float(close.rolling(50).mean().iloc[-1])

        score = 50

        # trend kontrolü
        if price > ma20:
            score += 10

        if price > ma50:
            score += 10

        if ma20 > ma50:
            score += 10

        # momentum
        momentum = close.pct_change(10).iloc[-1]

        if momentum > 0.05:
            score += 10

        # hacim artışı
        if volume.iloc[-1] > volume.mean():
            score += 10

        return score

    except Exception as e:

        print(symbol, "AI skor hatası:", e)

        return None
