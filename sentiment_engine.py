from sentiment_sources import get_market_news


POSITIVE_WORDS = [
    "gain",
    "growth",
    "surge",
    "rise",
    "strong",
    "record",
    "bull"
]

NEGATIVE_WORDS = [
    "drop",
    "fall",
    "crash",
    "weak",
    "decline",
    "loss",
    "bear"
]


def analyze_sentiment():

    news = get_market_news()

    score = 0

    for title in news:

        text = title.lower()

        for word in POSITIVE_WORDS:

            if word in text:
                score += 1

        for word in NEGATIVE_WORDS:

            if word in text:
                score -= 1

    if score > 2:
        return "BULLISH"

    if score < -2:
        return "BEARISH"

    return "NEUTRAL"
