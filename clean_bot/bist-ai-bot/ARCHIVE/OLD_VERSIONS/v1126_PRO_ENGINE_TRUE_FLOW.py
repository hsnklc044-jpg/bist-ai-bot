# =========================================
# FILE: v1126_PRO_ENGINE_TRUE_FLOW.py
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
last_update_time = {}

def val(x):
    try:
        return float(x.iloc[0]) if hasattr(x, "iloc") else float(x)
    except:
        return np.nan

# ================= DATA =================
def get_price(symbol):
    # 1m dene
    df1 = yf.download(symbol, period="1d", interval="1m", progress=False)
    if df1 is not None and not df1.empty:
        return val(df1["Close"].iloc[-1]), df1

    # fallback 5m
    df2 = yf.download(symbol, period="5d", interval="5m", progress=False)
    if df2 is not None and not df2.empty:
        return val(df2["Close"].iloc[-1]), df2

    return None, None

# ================= ATR =================
def atr(df):
    tr = np.maximum(df["High"] - df["Low"],
                    np.maximum(abs(df["High"] - df["Close"].shift()),
                               abs(df["Low"] - df["Close"].shift())))
    return val(tr.rolling(ATR_PERIOD).mean().iloc[-1])

# ================= SIGNAL =================
def signal(df):
    close = df["Close"]
    ma = close.rolling(20).mean()

    return val(close.iloc[-1]) > val(ma.iloc[-1])

# ================= SIZE =================
def size(atr_val):
    if atr_val == 0 or np.isnan(atr_val):
        return 0
    return round((ACCOUNT * RISK) / atr_val, 2)

print("🚀 PRO ENGINE (TRUE FLOW) STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    for s in SYMBOLS:
        price, df = get_price(s)

        if price is None or df is None or len(df) < 50:
            continue

        # ================= FREEZE DETECTION =================
        if s in last_price:
            if abs(price - last_price[s]) < 0.0001:
                # fiyat değişmedi
                if s in last_update_time:
                    diff = (now - last_update_time[s]).seconds

                    if diff > 60:
                        print(f"⚠️ DATA FREEZE {s} ({diff}s)")
                continue

        last_price[s] = price
        last_update_time[s] = now

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

            print(f"📊 {s} | price:{price:.2f} | PnL:{pnl:.2f}")

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