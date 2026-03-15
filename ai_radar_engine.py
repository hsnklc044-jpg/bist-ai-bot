import yfinance as yf
import pandas as pd
import numpy as np
import time

from bist_stocks import BIST_STOCKS


def get_data(symbol):
    try:
        ticker = symbol + ".IS"

        df = yf.download(
            ticker,
            period="6mo",
            interval="1d",
            progress=False
        )

        if df is None or len(df) < 60:
            return None

        df = df.dropna()
        return df

    except:
        return None


def compute_indicators(df):

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    tr1 = df["High"] - df["Low"]
    tr2 = abs(df["High"] - df["Close"].shift())
    tr3 = abs(df["Low"] - df["Close"].shift())

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(14).mean()

    return df


def score_stock(symbol):

    df = get_data(symbol)

    if df is None:
        return None

    try:

        df = compute_indicators(df)

        last = df.iloc[-1]

        score = 0

        # Trend
        if last["EMA20"] > last["EMA50"]:
            score += 30

        # Volume momentum
        volume = df["Volume"].iloc[-1]
        volume_avg = df["Volume"].rolling(20).mean().iloc[-1]

        if volume > volume_avg:
            score += 20

        # RSI momentum
        if 50 < last["RSI"] < 70:
            score += 20

        # Breakout
        recent_high = df["High"].rolling(20).max().iloc[-2]

        if last["Close"] > recent_high:
            score += 20

        # Volatility
        if last["ATR"] / last["Close"] > 0.02:
            score += 10

        return int(score)

    except:
        return None


def radar_scan():

    results = []

    for stock in BIST_STOCKS:

        score = score_stock(stock)

        if score is None:
            continue

        results.append((stock, score))

        time.sleep(0.25)

    if len(results) == 0:
        return []

    results = sorted(results, key=lambda x: x[1], reverse=True)

    return results[:10]
