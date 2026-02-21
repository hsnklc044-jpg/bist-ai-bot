import pandas as pd

def calculate_score(df: pd.DataFrame):
    score = 0

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    close = latest["Close"]
    ma20 = latest["MA20"]
    ma50 = latest["MA50"]
    rsi = latest["RSI"]
    volume = latest["Volume"]
    vol_avg = latest["VOL_AVG20"]

    # -----------------
    # TREND
    # -----------------
    if close > ma20:
        score += 1
    if close > ma50:
        score += 1
    if ma20 > ma50:
        score += 1
    if ma50 > prev["MA50"]:
        score += 1

    # -----------------
    # MOMENTUM
    # -----------------
    if 50 < rsi <= 65:
        score += 1
    elif 65 < rsi <= 75:
        score += 2
    elif rsi > 75:
        score += 1

    if rsi > prev["RSI"]:
        score += 1

    # -----------------
    # HACİM
    # -----------------
    if volume > vol_avg:
        score += 1
    if volume > vol_avg * 1.5:
        score += 2

    # -----------------
    # BREAKOUT
    # -----------------
    df["HH20"] = df["Close"].rolling(20).max()
    if close >= latest["HH20"]:
        score += 2

    # -----------------
    # SİNYAL
    # -----------------
    if score >= 10:
        signal = "KURUMSAL BREAKOUT"
    elif score >= 8:
        signal = "GÜÇLÜ"
    elif score >= 5:
        signal = "NÖTR"
    else:
        signal = "ZAYIF"

    return score, signal
