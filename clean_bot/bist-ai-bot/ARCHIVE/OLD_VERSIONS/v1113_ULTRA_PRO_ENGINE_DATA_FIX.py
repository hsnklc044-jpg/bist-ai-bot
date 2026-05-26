# =========================================
# FILE: v1113_ULTRA_PRO_ENGINE_DATA_FIX.py
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

# ================= SAFE FETCH =================
def get_data(symbol):
    for i in range(MAX_RETRY):
        try:
            df = yf.download(symbol, period="1d", interval="1m", progress=False)

            if df is not None and not df.empty:
                return df

        except:
            pass

        time.sleep(1)

    print(f"❌ DATA FAIL: {symbol}")
    return None

# ================= FALLBACK =================
def get_data_fallback(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="5m", progress=False)

        if df is not None and not df.empty:
            print(f"⚠️ FALLBACK USED: {symbol}")
            return df
    except:
        pass

    return None

# ================= SIGNAL =================
def simple_signal(df):
    close = df["Close"]
    ma = close.rolling(20).mean()

    if len(close) < 20:
        return None

    if float(close.iloc[-1]) > float(ma.iloc[-1]):
        return "LONG"

    return None

print("🚀 ULTRA PRO ENGINE (DATA FIX) STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    for symbol in SYMBOLS:

        df = get_data(symbol)

        # ❌ veri yoksa fallback
        if df is None:
            df = get_data_fallback(symbol)

        # ❌ hala yoksa geç
        if df is None or df.empty:
            continue

        signal = simple_signal(df)

        if signal and symbol not in positions:
            price = float(df["Close"].iloc[-1])

            positions[symbol] = price

            print(f"🚀 {signal} {symbol} | price:{price:.2f}")

    time.sleep(SCAN_INTERVAL)