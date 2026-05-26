# =========================================
# FILE: v1135_PRO_ENGINE_TRUE_FLOW.py
# =========================================

import yfinance as yf
import numpy as np
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]
SCAN_INTERVAL = 15

last_price = {}
last_update = {}
last_seen_time = {}

FREEZE_LIMIT = 90  # saniye

# ================= MARKET HOURS =================
def market_open():
    now = datetime.now()
    h, m = now.hour, now.minute

    if h < 10 or h > 18:
        return False
    if h == 18 and m > 10:
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
print("🚀 TRUE FLOW ENGINE STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    if not market_open():
        print("🛑 MARKET CLOSED")
        time.sleep(60)
        continue

    for s in SYMBOLS:
        df = get_data(s)
        time.sleep(2)

        if df is None:
            print(f"⚠️ NO DATA {s}")
            continue

        price = val(df["Close"])
        candle_time = df.index[-1]

        # INIT
        if s not in last_price:
            last_price[s] = price
            last_update[s] = now
            last_seen_time[s] = candle_time
            print(f"🆕 INIT {s} | {price:.2f}")
            continue

        # ================= FLOW =================
        if abs(price - last_price[s]) > 0.0001:
            print(f"🚀 FLOW {s} | {price:.2f}")
            last_price[s] = price
            last_update[s] = now
            last_seen_time[s] = candle_time
            continue

        # ================= NEW CANDLE =================
        if candle_time != last_seen_time[s]:
            print(f"🟡 IDLE (NEW CANDLE) {s} | {price:.2f}")
            last_seen_time[s] = candle_time
            last_update[s] = now
            continue

        # ================= FREEZE =================
        diff = (now - last_update[s]).seconds

        if diff > FREEZE_LIMIT:
            print(f"❌ DATA FREEZE {s} ({diff}s)")
        else:
            print(f"🟡 IDLE {s} ({diff}s)")

    time.sleep(SCAN_INTERVAL)