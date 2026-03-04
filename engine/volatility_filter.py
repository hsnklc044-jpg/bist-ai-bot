import pandas as pd
import numpy as np


VOL_LOOKBACK = 20
MAX_VOLATILITY = 0.08


def calculate_volatility(df):

    df["returns"] = df["Close"].pct_change()

    volatility = df["returns"].rolling(VOL_LOOKBACK).std().iloc[-1]

    return volatility


def volatility_filter(df):

    if len(df) < VOL_LOOKBACK:
        return False

    vol = calculate_volatility(df)

    if vol > MAX_VOLATILITY:
        return False

    return True
