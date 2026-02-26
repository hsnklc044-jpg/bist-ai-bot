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

        # Close'u garanti düz hale getir
        close = pd.Series(df["close"]).astype(float).values

        # RSI hesapla
        rsi_series = calculate_rsi(pd.Series(close))
        rsi = rsi_series.values

        if len(close) < 20 or len(rsi) < 20:
            continue

        latest_close = float(close[-1])
        latest_rsi = float(rsi[-1])

        ma20 = float(pd.Series(close).rolling(20).mean().iloc[-1])
        momentum = latest_close - float(close[-5])

        score = 0

        if latest_close > ma20:
            score += 1

        if latest_rsi > 50:
            score += 1

        if momentum > 0:
            score += 1

        results.append({
            "symbol": symbol.replace(".IS", ""),
            "rsi": round(latest_rsi, 2),
            "score": score
        })

    sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)

    return sorted_results[:3]
