# =========================================
# FILE: v1134_PRO_ENGINE_MARKET_AWARE.py
# =========================================

import yfinance as yf
import numpy as np
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]
SCAN_INTERVAL = 20

last_price = {}
last_update = {}

# ================= MARKET HOURS =================
def market_open():
    now = datetime.now()
    hour = now.hour
    minute = now.minute

    # BIST 10:00 - 18:00
    if hour < 10 or hour > 18:
        return False

    if hour == 18 and minute > 10:
        return False

    return True

# ================= SAFE VALUE =================
def val(x):
    try:
        return float(np.ravel(x)[-1])
    except:
        return np.nan

# ================= DATA =================
def get_data(symbol):
    try:
        df = yf.download(
            symbol,
            period="5d",
            interval="1m",
            progress=False,
            threads=False
        )
        return df if df is not None and not df.empty else None
    except:
        return None

# ================= ENGINE =================
print("🚀 MARKET AWARE ENGINE STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    # 🔥 MARKET CONTROL
    if not market_open():
        print("🛑 MARKET CLOSED → NO FLOW EXPECTED")
        time.sleep(60)
        continue

    for s in SYMBOLS:
        df = get_data(s)
        time.sleep(2)

        if df is None:
            continue

        price = val(df["Close"])

        if s in last_price:
            if abs(price - last_price[s]) < 0.0001:
                diff = (now - last_update[s]).seconds
                print(f"⚠️ NO FLOW {s} ({diff}s)")
                continue

        print(f"✅ FLOW {s} | {price:.2f}")

        last_price[s] = price
        last_update[s] = now

    time.sleep(SCAN_INTERVAL)