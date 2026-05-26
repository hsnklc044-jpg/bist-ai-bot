# =========================================
# FILE: v1140_PRO_ENGINE_LIVE_FILTER.py
# =========================================

import yfinance as yf
import numpy as np
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

SCAN_INTERVAL = 15
ENTRY_THRESHOLD = 0.75
MIN_MOVE = 0.001  # %0.1 hareket şart

positions = {}
last_price = {}

def val(x):
    try:
        return float(np.ravel(x)[-1])
    except:
        return np.nan

def get_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False)
        return df if df is not None and not df.empty else None
    except:
        return None

# ================= SIGNAL =================
def signal(df):
    close = df["Close"]
    volume = df["Volume"]

    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()

    price = val(close.iloc[-1])
    ma20_v = val(ma20.iloc[-1])
    ma50_v = val(ma50.iloc[-1])

    momentum = price - val(close.iloc[-5])
    vol_strength = val(volume.iloc[-1]) / (val(volume.rolling(20).mean().iloc[-1]) + 1e-9)

    score = 0

    if price > ma20_v > ma50_v:
        score += 0.4
    if momentum > 0:
        score += 0.3
    if vol_strength > 1.2:
        score += 0.3

    return score

# ================= ENGINE =================
print("🚀 LIVE FILTER ENGINE STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    for s in SYMBOLS:
        df = get_data(s)
        time.sleep(2)

        if df is None or len(df) < 60:
            continue

        price = val(df["Close"].iloc[-1])
        score = signal(df)

        # ================= PRICE FILTER =================
        if s in last_price:
            move = abs(price - last_price[s]) / (last_price[s] + 1e-9)

            if move < MIN_MOVE:
                print(f"⏸ SKIP {s} | no real move")
                continue

        last_price[s] = price

        # ================= ENTRY =================
        if s not in positions:
            if score >= ENTRY_THRESHOLD:
                positions[s] = {
                    "entry": price,
                    "max_price": price
                }
                print(f"🚀 ENTRY {s} | {price:.2f} | score:{score:.2f}")
            continue

        # ================= POSITION =================
        pos = positions[s]
        pnl = price - pos["entry"]
        pos["max_price"] = max(pos["max_price"], price)

        # TRAIL STOP
        if price < pos["max_price"] * 0.995:
            print(f"❌ EXIT {s} | TRAIL | PnL:{pnl:.2f}")
            del positions[s]
            continue

        print(f"📊 {s} | price:{price:.2f} | pnl:{pnl:.2f}")

    time.sleep(SCAN_INTERVAL)