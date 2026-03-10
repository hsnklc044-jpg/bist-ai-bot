import pandas as pd


def calculate_score(df):

    score = 0

    # EMA TREND
    df["EMA20"] = df["Close"].ewm(span=20).mean()

    if df["Close"].iloc[-1] > df["EMA20"].iloc[-1]:
        score += 3

    # RSI
    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    rsi_last = rsi.iloc[-1]

    if 50 < rsi_last < 70:
        score += 2

    # MOMENTUM
    if df["Close"].iloc[-1] > df["Close"].iloc[-5]:
        score += 2

    # VOLUME
    avg_volume = df["Volume"].rolling(20).mean().iloc[-1]

    if df["Volume"].iloc[-1] > avg_volume:
        score += 2

    # BREAKOUT
    highest = df["High"].rolling(20).max().iloc[-1]

    if df["Close"].iloc[-1] >= highest * 0.99:
        score += 1

    return score