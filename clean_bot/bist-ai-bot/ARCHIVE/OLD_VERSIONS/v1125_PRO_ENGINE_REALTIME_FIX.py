# =========================================
# FILE: v1125_PRO_ENGINE_REALTIME_FIX.py
# =========================================

import yfinance as yf
import numpy as np
import time
from datetime import datetime, timedelta

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

ACCOUNT = 10000
RISK = 0.01
ATR_PERIOD = 14
SCAN_INTERVAL = 5

positions = {}
last_prices = {}

def val(x):
    try:
        return float(x.iloc[0]) if hasattr(x, "iloc") else float(x)
    except:
        return np.nan

def get_data(symbol):
    # 1m dene
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False)
        if df is not None and not df.empty:
            return df
    except:
        pass

    # fallback
    try:
        df = yf.download(symbol, period="5d", interval="5m", progress=False)
        if df is not None and not df.empty:
            return df
    except:
        pass

    return None

def atr(df):
    tr = np.maximum(df["High"] - df["Low"],
                    np.maximum(abs(df["High"] - df["Close"].shift()),
                               abs(df["Low"] - df["Close"].shift())))
    return val(tr.rolling(ATR_PERIOD).mean().iloc[-1])

def signal(df):
    close = df["Close"]
    ma = close.rolling(20).mean()

    price = val(close.iloc[-1])
    ma_val = val(ma.iloc[-1])

    if price > ma_val:
        return True
    return False

def size(atr_val):
    if atr_val == 0 or np.isnan(atr_val):
        return 0
    return round((ACCOUNT * RISK) / atr_val, 2)

print("🚀 PRO ENGINE (REALTIME FIX) STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    for s in SYMBOLS:
        df = get_data(s)
        if df is None or len(df) < 50:
            continue

        price = val(df["Close"].iloc[-1])

        # ================= FLAT FILTER =================
        if s in last_prices:
            if abs(price - last_prices[s]) < 0.0001:
                continue  # fiyat değişmemiş → skip

        last_prices[s] = price

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

            print(f"🚀 ENTRY {s} | price:{price:.2f}")

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