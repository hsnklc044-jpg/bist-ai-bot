import pandas as pd
import numpy as np


def calculate_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


def score_stock(df):

    try:

        close = df["Close"]
        volume = df["Volume"]

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        if isinstance(volume, pd.DataFrame):
            volume = volume.iloc[:, 0]

        close = pd.to_numeric(close, errors="coerce").dropna()
        volume = pd.to_numeric(volume, errors="coerce").dropna()

        if len(close) < 60:
            return None

        price = close.iloc[-1]

        ma20 = close.rolling(20).mean().iloc[-1]
        ma50 = close.rolling(50).mean().iloc[-1]

        rsi = calculate_rsi(close).iloc[-1]

        momentum = close.pct_change(10).iloc[-1]

        avg_volume = volume.mean()

        score = 50

        # Trend
        if price > ma20:
            score += 10

        if price > ma50:
            score += 10

        if ma20 > ma50:
            score += 10

        # Momentum
        if pd.notna(momentum) and momentum > 0.05:
            score += 10

        # RSI momentum
        if pd.notna(rsi) and rsi > 55:
            score += 5

        if pd.notna(rsi) and rsi > 65:
            score += 5

        # Volume spike
        if volume.iloc[-1] > avg_volume * 1.5:
            score += 10

        score = min(score, 100)

        return int(score)

    except Exception as e:

        print("AI scoring hata:", e)

        return None
