
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

    if df is None or df.empty:
        return None

    df = df.copy()

    df["rsi"] = calculate_rsi(df["close"])

    if df["rsi"].iloc[-1] is None:
        return None

    last_close = float(df["close"].iloc[-1])
    last_rsi = float(df["rsi"].iloc[-1])

    if np.isnan(last_rsi):
        return None

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
