# =========================================
# FILE: v1131_PRO_ENGINE_ZERO_WARNING.py
# =========================================

import yfinance as yf
import numpy as np
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

ACCOUNT = 10000
RISK = 0.01
ATR_PERIOD = 14
SCAN_INTERVAL = 5

positions = {}
last_price = {}
last_update = {}

# ================= SAFE VALUE =================
def val(x):
    try:
        return float(np.ravel(x)[-1])
    except:
        try:
            return float(x)
        except:
            return np.nan

# ================= MARKET =================
def market_open():
    now = datetime.now()
    return 10 <= now.hour < 18

# ================= DATA =================
def get_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False)
        if df is not None and not df.empty:
            return df
    except:
        pass
    return None

# ================= ATR =================
def atr(df):
    h = np.ravel(df["High"])
    l = np.ravel(df["Low"])
    c = np.ravel(df["Close"])

    tr = np.maximum(h - l, np.maximum(abs(h - np.roll(c, 1)), abs(l - np.roll(c, 1))))
    return float(np.mean(tr[-ATR_PERIOD:]))

# ================= SIGNAL =================
def signal(df):
    close = np.ravel(df["Close"])
    ma = np.mean(close[-20:])
    return close[-1] > ma

# ================= SIZE =================
def size(atr_val):
    if atr_val == 0 or np.isnan(atr_val):
        return 0
    return round((ACCOUNT * RISK) / atr_val, 2)

print("🚀 PRO ENGINE (ZERO WARNING) STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    if not market_open():
        print("🛑 MARKET CLOSED")
        time.sleep(60)
        continue

    for s in SYMBOLS:
        df = get_data(s)

        if df is None or len(df) < 50:
            continue

        price = val(df["Close"])

        # ================= FREEZE =================
        if s in last_price:
            if abs(price - last_price[s]) < 0.0001:
                diff = (now - last_update[s]).seconds
                if diff > 60:
                    print(f"⚠️ FREEZE {s} ({diff}s)")
                continue

        last_price[s] = price
        last_update[s] = now

        atr_val = atr(df)

        # ================= ENTRY =================
        if s not in positions:
            if not signal(df):
                continue

            pos_size = size(atr_val)
            if pos_size <= 0:
                continue

            positions[s] = {
                "entry": price,
                "size": pos_size,
                "sl": price - atr_val,
                "tp": price + atr_val * 2,
                "max_price": price
            }

            print(f"🚀 ENTRY {s} | {price:.2f}")

        # ================= MONITOR =================
        else:
            pos = positions[s]

            pnl = (price - pos["entry"]) * pos["size"]
            pos["max_price"] = max(pos["max_price"], price)

            print(f"📊 {s} | {price:.2f} | PnL:{pnl:.2f}")

            trailing = pos["max_price"] - atr_val

            if price <= pos["sl"]:
                reason = "SL"
            elif price >= pos["tp"]:
                reason = "TP"
            elif price <= trailing:
                reason = "TRAIL"
            else:
                continue

            print(f"❌ EXIT {s} | {reason} | PnL:{pnl:.2f}")
            del positions[s]

    time.sleep(SCAN_INTERVAL)