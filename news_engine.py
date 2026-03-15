import yfinance as yf


def analyze_news(symbol):

    try:

        ticker = yf.Ticker(symbol + ".IS")

        news = ticker.news

        if not news:
            return None

        title = news[0]["title"].lower()

        score = 50

        positive_words = ["growth","contract","profit","increase","deal"]
        negative_words = ["loss","decline","investigation","drop","risk"]

        for word in positive_words:
            if word in title:
                score += 10

        for word in negative_words:
            if word in title:
                score -= 10

        if score > 60:
            sentiment = "Bullish"
        elif score < 40:
            sentiment = "Bearish"
        else:
            sentiment = "Neutral"

        return {
            "symbol": symbol,
            "sentiment": sentiment,
            "score": score
        }

    except:
        return None
