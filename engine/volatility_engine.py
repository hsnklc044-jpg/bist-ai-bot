import pandas as pd


def volatility_score(close, high, low):

    if len(close) < 20:
        return 0

    score = 0

    # ATR hesaplama
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(14).mean()

    # ATR düşüşü → squeeze
    if atr.iloc[-1] < atr.tail(10).mean():
        score += 2

    # breakout pressure
    price_range = close.tail(10).max() - close.tail(10).min()

    if price_range / close.iloc[-1] < 0.04:
        score += 2

    return score
