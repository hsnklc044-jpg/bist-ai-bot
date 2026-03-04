import pandas as pd
import numpy as np

RS_PERIOD = 60


def add_indicators(df):

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    df["EMA200"] = df["Close"].ewm(span=200).mean()

    df["Momentum"] = df["Close"].pct_change(RS_PERIOD)

    df["VolumeAvg"] = df["Volume"].rolling(20).mean()

    return df


def score_stock(df):

    row = df.iloc[-1]

    score = 0

    # Trend
    if row["EMA20"] > row["EMA50"]:
        score += 20

    if row["EMA50"] > row["EMA200"]:
        score += 20

    # Momentum
    if row["Momentum"] > 0:
        score += 20

    # Volume Expansion
    if row["Volume"] > row["VolumeAvg"] * 1.5:
        score += 20

    # Price strength
    recent_high = df["Close"].rolling(50).max().iloc[-1]

    if row["Close"] > recent_high * 0.9:
        score += 20

    return score


def radar_scan(data):

    results = []

    for symbol, df in data.items():

        df = add_indicators(df)

        score = score_stock(df)

        results.append((symbol, score))

    results = sorted(results, key=lambda x: x[1], reverse=True)

    return results
