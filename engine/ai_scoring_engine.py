import pandas as pd


def score_stock(df):

    try:

        close = df["Close"].astype(float)
        volume = df["Volume"].astype(float)

        # son fiyat
        price = close.iloc[-1]

        # moving averages
        ma20 = close.rolling(20).mean().iloc[-1]
        ma50 = close.rolling(50).mean().iloc[-1]

        score = 50

        # trend
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

        # volume spike
        if volume.iloc[-1] > volume.mean():
            score += 10

        return int(score)

    except Exception as e:

        print("AI scoring hata:", e)

        return None
