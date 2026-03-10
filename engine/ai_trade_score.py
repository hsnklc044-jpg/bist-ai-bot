import pandas as pd


def calculate_rsi(df, period=14):

    delta = df["Close"].diff()

    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss

    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]


def calculate_trade_score(df):

    score = 0

    try:

        close = df["Close"]

        ema20 = close.ewm(span=20).mean().iloc[-1]
        ema50 = close.ewm(span=50).mean().iloc[-1]

        rsi = calculate_rsi(df)

        volume_avg = df["Volume"].rolling(20).mean().iloc[-1]
        volume_now = df["Volume"].iloc[-1]

        price = close.iloc[-1]

        # TREND
        if ema20 > ema50:
            score += 30

        # MOMENTUM
        if rsi > 55:
            score += 20

        if rsi > 65:
            score += 10

        # VOLUME
        if volume_now > volume_avg * 1.5:
            score += 20

        # PRICE ABOVE EMA
        if price > ema20:
            score += 10

        # STRONG BREAKOUT
        recent_high = close.rolling(20).max().iloc[-2]

        if price > recent_high:
            score += 10

        return min(score, 100)

    except Exception as e:

        print("Trade score error:", e)

        return 0
