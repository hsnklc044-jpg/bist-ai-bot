import pandas as pd


def ai_score(df):

    score = 0

    try:

        close = df["Close"]

        ma20 = close.rolling(20).mean()
        ma50 = close.rolling(50).mean()

        last_close = close.iloc[-1]
        last_ma20 = ma20.iloc[-1]
        last_ma50 = ma50.iloc[-1]

        # Trend kontrolü
        if last_close > last_ma20:
            score += 1

        if last_close > last_ma50:
            score += 1

        # Momentum
        if ma20.iloc[-1] > ma20.iloc[-2]:
            score += 1

        if ma50.iloc[-1] > ma50.iloc[-2]:
            score += 1

        # Higher high kontrolü
        recent_high = close.tail(20).max()

        if last_close >= recent_high * 0.97:
            score += 2

        # Dipten dönüş
        recent_low = close.tail(20).min()

        if last_close > recent_low * 1.05:
            score += 1

    except Exception as e:

        print("AI scoring error:", e)

    return score
