# =========================================
# FILE: v1112_AI_SCORING_ENGINE.py
# =========================================

import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

ACCOUNT = 10000
RISK_PER_TRADE = 0.01
MAX_POSITION_PCT = 0.10
ATR_PERIOD = 14
SCAN_INTERVAL = 5
MAX_TRADES = 2

positions = {}

def val(x):
    try:
        return float(x.iloc[0]) if hasattr(x, "iloc") else float(x)
    except:
        return np.nan

def get_data(symbol):
    try:
        return yf.download(symbol, period="1d", interval="1m", progress=False)
    except:
        return None

# ================= AI SCORE =================
def ai_score(df):
    close = df["Close"]

    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()

    # TREND
    trend = 1 if val(close.iloc[-1]) > val(ma50.iloc[-1]) else 0

    # MOMENTUM
    momentum = val(close.iloc[-1]) - val(close.iloc[-5])
    momentum_score = 1 if momentum > 0 else 0

    # VOLATILITY
    vol = close.pct_change().rolling(20).std()
    vol_score = 1 if val(vol.iloc[-1]) > 0.002 else 0

    # VOLUME
    volume = df["Volume"]
    vol_ma = volume.rolling(20).mean()
    volume_score = 1 if val(volume.iloc[-1]) > val(vol_ma.iloc[-1]) else 0

    total_score = trend + momentum_score + vol_score + volume_score

    return total_score / 4  # 0 → 1

# ================= ATR =================
def calculate_atr(df):
    df["tr"] = np.maximum(df["High"] - df["Low"],
                          np.maximum(abs(df["High"] - df["Close"].shift()),
                                     abs(df["Low"] - df["Close"].shift())))
    return val(df["tr"].rolling(ATR_PERIOD).mean().iloc[-1])

# ================= SIZE =================
def position_size(price, atr):
    if atr == 0 or np.isnan(atr):
        return 0

    risk_amount = ACCOUNT * RISK_PER_TRADE
    size_risk = risk_amount / atr

    max_value = ACCOUNT * MAX_POSITION_PCT
    size_cap = max_value / price

    return round(min(size_risk, size_cap), 2)

print("🚀 AI SCORING ENGINE STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    signals = []

    for s in SYMBOLS:
        df = get_data(s)
        if df is None or df.empty or len(df) < 50:
            continue

        score = ai_score(df)

        if score < 0.75:  # 🔥 sadece güçlüler
            continue

        price = val(df["Close"].iloc[-1])
        atr = calculate_atr(df)

        signals.append((s, price, atr, score))

    signals = sorted(signals, key=lambda x: x[3], reverse=True)[:MAX_TRADES]

    for s, price, atr, score in signals:
        if s in positions:
            continue

        size = position_size(price, atr)
        if size <= 0:
            continue

        positions[s] = {
            "entry": price,
            "size": size,
            "score": score
        }

        print(f"🚀 LONG {s} | price:{price:.2f} score:{score:.2f} size:{size}")

    time.sleep(SCAN_INTERVAL)