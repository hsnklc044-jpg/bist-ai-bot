# =========================================
# FILE: v1133_PRO_DATA_AWARE_ENGINE_PATCHED.py
# =========================================

import yfinance as yf
import numpy as np
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

SCAN_INTERVAL = 20

last_price = {}
last_update = {}

def val(x):
    try:
        return float(np.ravel(x)[-1])
    except:
        return np.nan

def get_data(symbol):
    try:
        df = yf.download(
            symbol,
            period="5d",           # 🔥 kritik değişim
            interval="1m",
            progress=False,
            threads=False
        )
        return df if df is not None and not df.empty else None
    except:
        return None

print("🚀 DATA FLOW PATCH ACTIVE")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    for s in SYMBOLS:
        df = get_data(s)
        time.sleep(2)  # 🔥 rate limit fix

        if df is None:
            continue

        price = val(df["Close"])

        if s in last_price:
            if abs(price - last_price[s]) < 0.0001:
                diff = (now - last_update[s]).seconds
                print(f"⚠️ NO DATA FLOW {s} ({diff}s)")
                continue

        print(f"✅ FLOW {s} | {price:.2f}")

        last_price[s] = price
        last_update[s] = now

    time.sleep(SCAN_INTERVAL)