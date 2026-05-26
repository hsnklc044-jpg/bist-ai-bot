# =========================================
# FILE: v1133_PRO_DATA_AWARE_ENGINE.py
# =========================================

import yfinance as yf
import numpy as np
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

ACCOUNT = 10000
RISK_PER_TRADE = 0.01
MAX_TOTAL_RISK = 0.03
ATR_PERIOD = 14
SCAN_INTERVAL = 15
MAX_POSITIONS = 2

positions = {}
last_trade_time = {}
last_price = {}
last_update = {}

# ================= SAFE =================
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
            period="1d",
            interval="1m",
            progress=False,
            threads=False  # daha stabil
        )
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

# ================= SCORE =================
def score(df):
    close = np.ravel(df["Close"])

    ma20 = np.mean(close[-20:])
    ma50 = np.mean(close[-50:])
    momentum = close[-1] - close[-5]

    trend = 1 if close[-1] > ma20 else 0
    strength = 1 if ma20 > ma50 else 0
    momentum_score = 1 if momentum > 0 else 0

    return trend + strength + momentum_score

# ================= SIZE =================
def position_size(atr_val):
    if atr_val == 0 or np.isnan(atr_val):
        return 0
    risk_amount = ACCOUNT * RISK_PER_TRADE
    return round(risk_amount / atr_val, 2)

# ================= TOTAL RISK =================
def total_risk():
    return sum(p["risk"] for p in positions.values())

# ================= MARKET =================
def market_open():
    now = datetime.now()
    return 10 <= now.hour < 18

print("🚀 v1133 PRO DATA AWARE ENGINE STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    if not market_open():
        print("🛑 MARKET CLOSED")
        time.sleep(60)
        continue

    candidates = []

    # ================= SCAN =================
    for s in SYMBOLS:
        df = get_data(s)
        time.sleep(1)  # rate limit fix

        if df is None or len(df) < 50:
            continue

        price = val(df["Close"])

        # ================= DATA FLOW CHECK =================
        if s in last_price:
            if abs(price - last_price[s]) < 0.0001:
                diff = (now - last_update[s]).seconds
                print(f"⚠️ NO DATA FLOW {s} ({diff}s)")
                continue

        last_price[s] = price
        last_update[s] = now

        sc = score(df)
        if sc < 2:
            continue

        atr_val = atr(df)
        candidates.append((s, sc, price, atr_val))

    # ================= SORT =================
    candidates = sorted(candidates, key=lambda x: x[1], reverse=True)

    # ================= ENTRY =================
    for s, sc, price, atr_val in candidates:

        if s in positions:
            continue

        if len(positions) >= MAX_POSITIONS:
            break

        if total_risk() >= ACCOUNT * MAX_TOTAL_RISK:
            print("⚠️ MAX RISK LIMIT")
            break

        if s in last_trade_time:
            diff = (now - last_trade_time[s]).seconds
            if diff < 120:
                continue

        size = position_size(atr_val)
        if size <= 0:
            continue

        risk = atr_val * size

        positions[s] = {
            "entry": price,
            "size": size,
            "sl": price - atr_val,
            "tp": price + atr_val * 2,
            "max_price": price,
            "risk": risk
        }

        last_trade_time[s] = now

        print(f"🚀 ENTRY {s} | price:{price:.2f} score:{sc}")

    # ================= MONITOR =================
    for s in list(positions.keys()):
        df = get_data(s)
        time.sleep(1)

        if df is None:
            continue

        price = val(df["Close"])
        atr_val = atr(df)
        pos = positions[s]

        pnl = (price - pos["entry"]) * pos["size"]
        pos["max_price"] = max(pos["max_price"], price)

        # ================= TRAILING =================
        trailing = pos["max_price"] - (atr_val * 1.2)

        print(f"📊 {s} | {price:.2f} | PnL:{pnl:.2f}")

        # ================= EXIT =================
        if price <= pos["sl"]:
            reason = "SL"

        elif price >= pos["tp"]:
            reason = "TP"

        elif price <= trailing and price > pos["entry"]:
            reason = "TRAIL_PROFIT"

        else:
            continue

        print(f"❌ EXIT {s} | {reason} | PnL:{pnl:.2f}")
        del positions[s]

    time.sleep(SCAN_INTERVAL)