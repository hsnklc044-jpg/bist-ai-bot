# =========================================
# FILE: v1138_PRO_ENGINE_TRADE_CORE_FIXED.py
# =========================================

import yfinance as yf
import numpy as np
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

SCAN_INTERVAL = 15
ENTRY_THRESHOLD = 0.5

positions = {}

# ================= SAFE FLOAT =================
def val(x):
    try:
        return float(np.ravel(x)[-1])
    except:
        return np.nan

# ================= DATA =================
def get_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False)
        return df if df is not None and not df.empty else None
    except:
        return None

# ================= SIGNAL =================
def signal(df):
    close = df["Close"]
    ma = close.rolling(20).mean()

    price = val(close.iloc[-1])
    ma_val = val(ma.iloc[-1])
    momentum = price - val(close.iloc[-5])

    score = 0

    if price > ma_val:
        score += 0.5
    if momentum > 0:
        score += 0.5

    return score

# ================= ENGINE =================
print("🚀 TRADE CORE ENGINE (FIXED) STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    for s in SYMBOLS:
        df = get_data(s)
        time.sleep(2)

        if df is None or len(df) < 30:
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
                print(f"🚀 ENTRY {s} | {price:.2f} | score:{score}")
            continue

        # ================= POSITION =================
        pos = positions[s]
        entry = pos["entry"]

        pnl = price - entry
        pos["max_price"] = max(pos["max_price"], price)

        # ================= TRAIL STOP =================
        if price < pos["max_price"] * 0.995:
            print(f"❌ EXIT {s} | TRAIL | PnL:{pnl:.2f}")
            del positions[s]
            continue

        print(f"📊 {s} | price:{price:.2f} | pnl:{pnl:.2f}")

    time.sleep(SCAN_INTERVAL)