# =========================================
# FILE: v1127_PRO_ENGINE_MARKET_AWARE.py
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

# ================= TIME FILTER =================
def market_open():
    now = datetime.now()
    return 10 <= now.hour < 18  # BIST saatleri approx

# ================= DATA =================
def get_price(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False)
        if df is not None and not df.empty:
            return float(df["Close"].iloc[-1]), df
    except:
        pass
    return None, None

# ================= ATR =================
def atr(df):
    tr = np.maximum(df["High"] - df["Low"],
                    np.maximum(abs(df["High"] - df["Close"].shift()),
                               abs(df["Low"] - df["Close"].shift())))
    return float(tr.rolling(ATR_PERIOD).mean().iloc[-1])

# ================= SIGNAL =================
def signal(df):
    close = df["Close"]
    ma = close.rolling(20).mean()
    return float(close.iloc[-1]) > float(ma.iloc[-1])

# ================= SIZE =================
def size(atr_val):
    if atr_val == 0 or np.isnan(atr_val):
        return 0
    return round((ACCOUNT * RISK) / atr_val, 2)

print("🚀 PRO ENGINE (MARKET AWARE) STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    # ================= MARKET CLOSED =================
    if not market_open():
        print("🛑 MARKET CLOSED → SLEEP MODE")
        time.sleep(60)
        continue

    for s in SYMBOLS:
        price, df = get_price(s)

        if price is None or df is None or len(df) < 50:
            continue

        # ================= FREEZE DETECTION =================
        if s in last_price:
            if abs(price - last_price[s]) < 0.0001:
                diff = (now - last_update[s]).seconds

                if diff > 60:
                    print(f"⚠️ FREEZE {s} ({diff}s) → SKIP")
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