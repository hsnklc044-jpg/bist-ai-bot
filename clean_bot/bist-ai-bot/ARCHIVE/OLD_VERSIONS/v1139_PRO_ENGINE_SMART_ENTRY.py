# =========================================
# FILE: v1139_PRO_ENGINE_SMART_ENTRY.py
# =========================================

import yfinance as yf
import numpy as np
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

SCAN_INTERVAL = 15
ENTRY_THRESHOLD = 0.75

positions = {}

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

# ================= SMART SIGNAL =================
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

    # TREND
    if price > ma20_v > ma50_v:
        score += 0.4

    # MOMENTUM
    if momentum > 0:
        score += 0.3

    # VOLUME
    if vol_strength > 1.2:
        score += 0.3

    return score

# ================= ENGINE =================
print("🚀 SMART ENTRY ENGINE STARTED")

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

        print(f"📊 {s} | price:{price:.2f} | pnl:{pnl:.2f} | score:{score:.2f}")

    time.sleep(SCAN_INTERVAL)