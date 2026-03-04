import pandas as pd
import numpy as np


def calculate_rsi(df, period=14):

    delta = df["Close"].diff()

    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_macd(df):

    exp1 = df["Close"].ewm(span=12, adjust=False).mean()
    exp2 = df["Close"].ewm(span=26, adjust=False).mean()

    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()

    return macd, signal


def volume_spike(df):

    avg_volume = df["Volume"].rolling(20).mean()

    if df["Volume"].iloc[-1] > avg_volume.iloc[-1] * 1.5:
        return True

    return False


def ema_trend(df):

    ema20 = df["Close"].ewm(span=20).mean()
    ema50 = df["Close"].ewm(span=50).mean()

    if ema20.iloc[-1] > ema50.iloc[-1]:
        return True

    return False


def relative_strength(df):

    returns = df["Close"].pct_change()

    strength = returns.rolling(20).mean()

    return strength.iloc[-1]


def score_stock(df):

    score = 0

    rsi = calculate_rsi(df)

    macd, signal = calculate_macd(df)

    # RSI MOMENTUM
    if 50 < rsi.iloc[-1] < 70:
        score += 20

    # MACD TREND
    if macd.iloc[-1] > signal.iloc[-1]:
        score += 20

    # EMA TREND
    if ema_trend(df):
        score += 25

    # VOLUME SPIKE
    if volume_spike(df):
        score += 20

    # RELATIVE STRENGTH
    rs = relative_strength(df)

    if rs > 0:
        score += 15

    return score
