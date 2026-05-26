# =========================================
# FILE: v1121_SMART_PORTFOLIO_ENGINE.py
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
MAX_POSITIONS = 2

positions = {}

def val(x):
    try:
        return float(x.iloc[0]) if hasattr(x, "iloc") else float(x)
    except:
        return np.nan

def get_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False)
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

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ================= SIGNAL SCORE =================
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

    # trend
    if price > ma_val:
        score += 0.4

    # mean reversion
    if price < ma_val - std_val:
        score += 0.4

    # RSI
    if rsi_val < 40:
        score += 0.2

    return score

def size(price, atr_val):
    if atr_val == 0 or np.isnan(atr_val):
        return 0
    return round((ACCOUNT * RISK) / atr_val, 2)

print("🚀 SMART PORTFOLIO ENGINE STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    candidates = []

    # ================= SCAN =================
    for s in SYMBOLS:
        if s in positions:
            continue

        df = get_data(s)
        if df is None or len(df) < 50:
            continue

        score = signal_score(df)

        if score > 0.5:
            candidates.append((s, score, df))

    # ================= SELECT BEST =================
    candidates = sorted(candidates, key=lambda x: x[1], reverse=True)

    for s, score, df in candidates:

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

        print(f"🚀 SELECTED {s} | score:{score:.2f}")

    # ================= MANAGEMENT =================
    for s in list(positions.keys()):
        df = get_data(s)
        if df is None:
            continue

        price = val(df["Close"].iloc[-1])
        pos = positions[s]

        pnl = (price - pos["entry"]) * pos["size"]

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

        del positions[s]

    time.sleep(SCAN_INTERVAL)