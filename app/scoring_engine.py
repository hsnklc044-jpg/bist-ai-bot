import pandas as pd

from engine.institutional_money_flow import institutional_score


def calculate_indicators(df):

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    df["EMA200"] = df["Close"].ewm(span=200).mean()

    df["momentum"] = df["Close"].pct_change(20)

    df["volume_avg"] = df["Volume"].rolling(20).mean()

    return df


def score_stock(df):

    score = 0

    df = calculate_indicators(df)

    latest = df.iloc[-1]

    # TREND
    if latest["EMA20"] > latest["EMA50"]:
        score += 15

    if latest["EMA50"] > latest["EMA200"]:
        score += 20

    # MOMENTUM
    if latest["momentum"] > 0:
        score += 15

    if latest["momentum"] > 0.10:
        score += 10

    # VOLUME EXPANSION
    if latest["Volume"] > 1.5 * latest["volume_avg"]:
        score += 15

    # BREAKOUT
    recent_high = df["Close"].rolling(20).max().iloc[-2]

    if latest["Close"] > recent_high:
        score += 15

    # INSTITUTIONAL FLOW
    score += institutional_score(df)

    return score
