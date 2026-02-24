# app/scanner.py

import pandas as pd
from app.data_utils import get_data
from app.bist30 import BIST30


def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def scan_market():

    results = []

    for symbol in BIST30:

        df = get_data(symbol=symbol, period="3mo")

        if df is None or df.empty:
            continue

        if "close" not in df.columns:
            continue

        if len(df) < 20:
            continue

        df["rsi"] = calculate_rsi(df["close"])

        latest = df.iloc[-1]

        score = 0

        # 20 günlük trend
        ma20 = df["close"].rolling(20).mean().iloc[-1]
        if latest["close"] > ma20:
            score += 1

        # RSI filtresi
        if latest["rsi"] > 50:
            score += 1

        # 5 günlük momentum
        momentum = latest["close"] - df["close"].iloc[-5]
        if momentum > 0:
            score += 1

        results.append({
            "symbol": symbol.replace(".IS", ""),
            "rsi": round(float(latest["rsi"]), 2),
            "score": score
        })

    sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)

    return sorted_results[:3]
