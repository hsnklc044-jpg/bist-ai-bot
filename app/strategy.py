import pandas as pd
import numpy as np


def calculate_rsi(series, period=14):
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    return rsi


def generate_signal(df):

    if df is None:
        return None

    if df.empty:
        return None

    df = df.copy()

    if "close" not in df.columns:
        return None

    df["rsi"] = calculate_rsi(df["close"])

    # Son değerleri scalar'a çevir
    last_close = df["close"].iloc[-1]
    last_rsi = df["rsi"].iloc[-1]

    if pd.isna(last_rsi):
        return None

    last_close = float(last_close)
    last_rsi = float(last_rsi)

    if last_rsi < 30:
        return {
            "side": "BUY",
            "price": last_close,
            "rsi": last_rsi
        }

    if last_rsi > 70:
        return {
            "side": "SELL",
            "price": last_close,
            "rsi": last_rsi
        }

    return None
