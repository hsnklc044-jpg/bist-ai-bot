import pandas as pd


def rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


def ai_score(close, volume):

    score = 0

    # TREND
    ma20 = close.tail(20).mean()
    ma50 = close.tail(50).mean()

    if ma20 > ma50:
        score += 3

    # MOMENTUM
    if close.iloc[-1] > close.iloc[-5]:
        score += 2

    # HACİM PATLAMASI
    avg_volume = volume.tail(20).mean()
    last_volume = volume.iloc[-1]

    if last_volume > avg_volume * 1.5:
        score += 2

    # RSI
    rsi_val = rsi(close).iloc[-1]

    if rsi_val > 55:
        score += 2

    # PULLBACK
    if close.iloc[-1] < close.max():
        score += 1

    return score
