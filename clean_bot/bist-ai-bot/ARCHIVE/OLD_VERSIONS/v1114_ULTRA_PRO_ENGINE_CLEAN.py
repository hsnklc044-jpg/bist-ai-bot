# =========================================
# FILE: v1114_ULTRA_PRO_ENGINE_CLEAN.py
# =========================================

import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

SCAN_INTERVAL = 5
MAX_RETRY = 3

positions = {}

# ================= SAFE VALUE =================
def val(x):
    try:
        return float(x.iloc[0]) if hasattr(x, "iloc") else float(x)
    except:
        return np.nan

# ================= DATA =================
def get_data(symbol):
    for _ in range(MAX_RETRY):
        try:
            df = yf.download(symbol, period="1d", interval="1m", progress=False)

            if df is not None and not df.empty:
                return df
        except:
            pass

        time.sleep(1)

    return None

def fallback_data(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="5m", progress=False)
        if df is not None and not df.empty:
            print(f"⚠️ FALLBACK: {symbol}")
            return df
    except:
        pass

    return None

# ================= SIGNAL =================
def signal(df):
    close = df["Close"]
    ma = close.rolling(20).mean()

    if len(close) < 20:
        return None

    if val(close.iloc[-1]) > val(ma.iloc[-1]):
        return "LONG"

    return None

print("🚀 CLEAN ENGINE STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    for symbol in SYMBOLS:

        df = get_data(symbol)

        if df is None:
            df = fallback_data(symbol)

        if df is None or df.empty:
            print(f"❌ NO DATA: {symbol}")
            continue

        sig = signal(df)

        if sig and symbol not in positions:
            price = val(df["Close"].iloc[-1])

            positions[symbol] = price

            print(f"🚀 {sig} {symbol} | price:{price:.2f}")

    time.sleep(SCAN_INTERVAL)