import pandas as pd


def calculate_rsi(series, period=14):
    if len(series) < period:
        return None

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    last_rsi = rsi.iloc[-1]

    if pd.isna(last_rsi):
        return None

    return last_rsi


def calculate_ema(series, period=50):
    if len(series) < period:
        return None

    ema = series.ewm(span=period, adjust=False).mean()
    return ema.iloc[-1]
