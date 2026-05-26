# =========================================
# FILE: v1120_ADAPTIVE_ENGINE_LIVE_ACTIVE.py
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

    try:
        return yf.download(symbol, period="5d", interval="5m", progress=False)
    except:
        return None

# ================= ATR =================
def atr(df):
    tr = np.maximum(df["High"] - df["Low"],
                    np.maximum(abs(df["High"] - df["Close"].shift()),
                               abs(df["Low"] - df["Close"].shift())))
    return val(tr.rolling(ATR_PERIOD).mean().iloc[-1])

# ================= RSI =================
def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ================= REGIME (FIXED) =================
def detect_regime():
    vols = []
    for s in SYMBOLS:
        df = get_data(s)
        if df is None:
            continue
        vol = val(df["Close"].pct_change().rolling(20).std().iloc[-1])
        if not np.isnan(vol):
            vols.append(vol)

    if not vols:
        return "QUIET"

    avg = np.mean(vols)

    # 🔥 DÜŞÜRÜLDÜ (kritik fix)
    if avg < 0.0004:
        return "QUIET"
    elif avg < 0.001:
        return "NORMAL"
    else:
        return "TREND"

# ================= STRATEGIES =================

def trend_signal(df):
    ma = df["Close"].rolling(20).mean()
    price = val(df["Close"].iloc[-1])
    ma_val = val(ma.iloc[-1])

    if price > ma_val:
        return "LONG"
    return None

def mean_reversion_signal(df):
    close = df["Close"]
    ma = close.rolling(20).mean()
    std = close.rolling(20).std()
    r = rsi(close)

    price = val(close.iloc[-1])
    lower = val((ma - 1.0 * std).iloc[-1])  # 🔥 daha agresif
    rsi_val = val(r.iloc[-1])

    momentum = price - val(close.iloc[-2])

    # 🔥 yumuşatılmış şart
    if price < lower or (rsi_val < 40 and momentum > 0):
        return "LONG"

    return None

# ================= SIZE =================
def size(price, atr_val):
    if atr_val == 0 or np.isnan(atr_val):
        return 0
    return round((ACCOUNT * RISK) / atr_val, 2)

print("🚀 ADAPTIVE ENGINE (ACTIVE MODE) STARTED")

while True:
    now = datetime.now()
    regime = detect_regime()

    print(f"\n⏱ {now} | REGIME: {regime}")

    for s in SYMBOLS:
        df = get_data(s)
        if df is None:
            continue

        price = val(df["Close"].iloc[-1])
        atr_val = atr(df)

        if s not in positions:

            # 🔥 QUIET'te bile trade üret
            if regime == "TREND":
                sig = trend_signal(df)
                tp_mult = 3
            elif regime == "QUIET":
                sig = mean_reversion_signal(df)
                tp_mult = 1.3
            else:
                sig = trend_signal(df) or mean_reversion_signal(df)
                tp_mult = 2

            if sig:
                pos_size = size(price, atr_val)
                if pos_size <= 0:
                    continue

                sl = price - atr_val
                tp = price + atr_val * tp_mult

                positions[s] = {
                    "entry": price,
                    "size": pos_size,
                    "sl": sl,
                    "tp": tp,
                    "max_price": price
                }

                print(f"🚀 {sig} {s} | {price:.2f} | {regime}")

        else:
            pos = positions[s]
            pnl = (price - pos["entry"]) * pos["size"]

            pos["max_price"] = max(pos["max_price"], price)
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