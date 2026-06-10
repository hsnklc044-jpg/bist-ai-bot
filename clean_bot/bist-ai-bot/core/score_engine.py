import pandas as pd


def calculate_score(close, high, low, volume):

    if len(close) < 50:
        return None

    ma20 = float(
        close.rolling(20).mean().iloc[-1]
    )

    ma50 = float(
        close.rolling(50).mean().iloc[-1]
    )

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    if avg_loss.iloc[-1] == 0:

        rsi = 100

    else:

        rs = (
            avg_gain.iloc[-1]
            /
            avg_loss.iloc[-1]
        )

        rsi = (
            100 -
            (100 / (1 + rs))
        )

    ema12 = close.ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = close.ewm(
        span=26,
        adjust=False
    ).mean()

    macd = (
        ema12.iloc[-1]
        -
        ema26.iloc[-1]
    )

    avg_volume = (
        volume
        .rolling(20)
        .mean()
        .iloc[-1]
    )

    if avg_volume <= 0:

        volume_ratio = 1

    else:

        volume_ratio = (
            volume.iloc[-1]
            /
            avg_volume
        )

    volatility = (
        close
        .pct_change()
        .std()
        * 100
    )

    bull_score = 0
    bear_score = 0

    if ma20 > ma50:
        bull_score += 25
    else:
        bear_score += 25

    if rsi < 30:
        bull_score += 20

    elif rsi < 40:
        bull_score += 10

    elif rsi > 80:
        bear_score += 15

    elif rsi > 70:
        bear_score += 10

    if macd > 0:
        bull_score += 15
    else:
        bear_score += 15

    if volume_ratio > 1.1:
        bull_score += 10

    elif volume_ratio < 0.8:
        bear_score += 10

    if volatility < 2:
        bull_score += 10

    elif volatility > 6:
        bear_score += 10

    raw_score = (
        bull_score
        -
        bear_score
    )

    score = (
        50
        +
        raw_score * 0.5
    )

    score = max(
        0,
        min(score, 100)
    )

    return round(score, 0)