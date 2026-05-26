# =========================================
# FILE: v1124_PRO_ENGINE_MONITORING.py
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
MAX_POSITIONS = 2
COOLDOWN_MINUTES = 10

positions = {}
cooldowns = {}

def val(x):
    try:
        return float(x.iloc[0]) if hasattr(x, "iloc") else float(x)
    except:
        return np.nan

def market_open():
    now = datetime.now()
    return 10 <= now.hour <= 18

def get_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False)
        if df is not None and not df.empty:
            return df
    except:
        pass

    try:
        df = yf.download(symbol, period="5d", interval="5m", progress=False)
        if df is not None and not df.empty:
            return df
    except:
        pass

    return None  # sessiz geç

def atr(df):
    tr = np.maximum(df["High"] - df["Low"],
                    np.maximum(abs(df["High"] - df["Close"].shift()),
                               abs(df["Low"] - df["Close"].shift())))
    return val(tr.rolling(ATR_PERIOD).mean().iloc[-1])

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def signal_score(df):
    close = df["Close"]
    ma = close.rolling(20).mean()
    std = close.rolling(20).std()
    r = rsi(close)

    price = val(close.iloc[-1])
    ma_val = val(ma.iloc[-1])
    std_val = val(std.iloc[-1])
    rsi_val = val(r.iloc[-1])

    score = 0
    if price > ma_val: score += 0.3
    if price < ma_val - std_val: score += 0.3
    if rsi_val < 45: score += 0.2
    if price > val(close.iloc[-3]): score += 0.2

    return score

def size(price, atr_val):
    if atr_val == 0 or np.isnan(atr_val):
        return 0
    return round((ACCOUNT * RISK) / atr_val, 2)

print("🚀 PRO ENGINE (LIVE MONITORING) STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    if not market_open():
        print("⛔ MARKET CLOSED")
        time.sleep(30)
        continue

    # ================= ENTRY =================
    candidates = []

    for s in SYMBOLS:
        if s in positions:
            continue
        if s in cooldowns and now < cooldowns[s]:
            continue

        df = get_data(s)
        if df is None or len(df) < 50:
            continue

        score = signal_score(df)
        candidates.append((s, score, df))

    if candidates:
        scores = [c[1] for c in candidates]
        threshold = max(0.3, np.mean(scores))

        filtered = [c for c in candidates if c[1] >= threshold]
        if not filtered:
            filtered = [max(candidates, key=lambda x: x[1])]

        filtered = sorted(filtered, key=lambda x: x[1], reverse=True)

        for s, score, df in filtered:
            if len(positions) >= MAX_POSITIONS:
                break

            price = val(df["Close"].iloc[-1])
            atr_val = atr(df)

            pos_size = size(price, atr_val)
            if pos_size <= 0:
                continue

            positions[s] = {
                "entry": price,
                "size": pos_size,
                "sl": price - atr_val,
                "tp": price + atr_val * 2,
                "max_price": price
            }

            print(f"🚀 ENTRY {s} | score:{score:.2f}")

    # ================= LIVE MONITOR =================
    for s in list(positions.keys()):
        df = get_data(s)
        if df is None:
            continue

        price = val(df["Close"].iloc[-1])
        pos = positions[s]

        pnl = (price - pos["entry"]) * pos["size"]

        print(f"📊 {s} | price:{price:.2f} | PnL:{pnl:.2f}")

        pos["max_price"] = max(pos["max_price"], price)
        trailing = pos["max_price"] - atr(df)

        if price <= pos["sl"]:
            reason = "SL"
        elif price >= pos["tp"]:
            reason = "TP"
        elif price <= trailing:
            reason = "TRAIL"
        else:
            continue

        print(f"❌ EXIT {s} | {reason} | PnL:{pnl:.2f}")

        cooldowns[s] = now + timedelta(minutes=COOLDOWN_MINUTES)
        del positions[s]

    time.sleep(SCAN_INTERVAL)