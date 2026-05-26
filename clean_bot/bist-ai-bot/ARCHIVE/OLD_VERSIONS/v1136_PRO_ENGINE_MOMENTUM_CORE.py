# =========================================
# FILE: v1136_PRO_ENGINE_MOMENTUM_CORE.py
# =========================================

import yfinance as yf
import numpy as np
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

SCAN_INTERVAL = 15
FREEZE_LIMIT = 90
IDLE_EXIT = 120

last_price = {}
last_update = {}
last_seen_time = {}

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
print("🚀 MOMENTUM CORE ENGINE STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    # MARKET CONTROL
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

        # ================= TIME =================
        idle_time = (now - last_update[s]).seconds

        # ================= IDLE EXIT =================
        if idle_time > IDLE_EXIT:
            print(f"⏸ EXIT MARKET {s} | NO MOMENTUM ({idle_time}s)")
            continue

        # ================= FREEZE =================
        if idle_time > FREEZE_LIMIT:
            print(f"❌ DATA FREEZE {s} ({idle_time}s)")
        else:
            print(f"🟡 IDLE {s} ({idle_time}s)")

    time.sleep(SCAN_INTERVAL)