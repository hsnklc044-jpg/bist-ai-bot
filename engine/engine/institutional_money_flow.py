import pandas as pd


VOLUME_LOOKBACK = 20
PRICE_LOOKBACK = 20


def detect_institutional_flow(df):

    if len(df) < VOLUME_LOOKBACK:
        return False

    df["volume_avg"] = df["Volume"].rolling(VOLUME_LOOKBACK).mean()

    latest = df.iloc[-1]

    volume_spike = latest["Volume"] > 2 * latest["volume_avg"]

    recent_high = df["Close"].rolling(PRICE_LOOKBACK).max().iloc[-2]

    breakout = latest["Close"] > recent_high

    if volume_spike and breakout:
        return True

    return False


def institutional_score(df):

    score = 0

    df["volume_avg"] = df["Volume"].rolling(20).mean()

    latest = df.iloc[-1]

    if latest["Volume"] > 1.5 * latest["volume_avg"]:
        score += 50

    recent_high = df["Close"].rolling(20).max().iloc[-2]

    if latest["Close"] > recent_high:
        score += 50

    return score
