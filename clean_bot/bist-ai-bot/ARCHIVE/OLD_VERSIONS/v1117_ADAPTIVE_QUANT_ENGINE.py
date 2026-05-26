# =========================================
# FILE: v1117_ADAPTIVE_QUANT_ENGINE.py
# =========================================

import yfinance as yf
import numpy as np
import pandas as pd
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

ACCOUNT = 10000
RISK_PER_TRADE = 0.01
ATR_PERIOD = 14
SCAN_INTERVAL = 5

positions = {}

# ================= SAFE =================
def val(x):
    try:
        return float(x.iloc[0]) if hasattr(x, "iloc") else float(x)
    except:
        return np.nan

# ================= DATA =================
def get_data(symbol):
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
            print(f"⚠️ FALLBACK: {symbol}")
            return df
    except:
        pass

    return None

# ================= ATR =================
def atr(df):
    tr = np.maximum(df["High"] - df["Low"],
                    np.maximum(abs(df["High"] - df["Close"].shift()),
                               abs(df["Low"] - df["Close"].shift())))
    return val(tr.rolling(ATR_PERIOD).mean().iloc[-1])

# ================= REGIME =================
def detect_regime():
    vols = []

    for s in SYMBOLS:
        df = get_data(s)
        if df is None:
            continue

        ret = df["Close"].pct_change()
        vol = val(ret.rolling(20).std().iloc[-1])

        if not np.isnan(vol):
            vols.append(vol)

    if not vols:
        return "QUIET"

    avg_vol = np.mean(vols)

    if avg_vol < 0.001:
        return "QUIET"
    elif avg_vol < 0.002:
        return "NORMAL"
    else:
        return "TREND"

# ================= ADAPTIVE PARAMS =================
def get_params(regime):
    if regime == "QUIET":
        return {
            "sl_mult": 1.0,
            "tp_mult": 1.5,
            "min_atr_pct": 0.001,
            "min_tp_pct": 0.003,
            "max_positions": 1
        }
    elif regime == "NORMAL":
        return {
            "sl_mult": 1.0,
            "tp_mult": 2.0,
            "min_atr_pct": 0.002,
            "min_tp_pct": 0.005,
            "max_positions": 2
        }
    else:  # TREND
        return {
            "sl_mult": 1.2,
            "tp_mult": 3.0,
            "min_atr_pct": 0.003,
            "min_tp_pct": 0.008,
            "max_positions": 3
        }

# ================= SIGNAL =================
def signal_score(df):
    close = df["Close"]
    ma20 = close.rolling(20).mean()

    trend = 1 if val(close.iloc[-1]) > val(ma20.iloc[-1]) else 0
    momentum = 1 if val(close.iloc[-1]) > val(close.iloc[-5]) else 0

    volume = df["Volume"]
    vol_ma = volume.rolling(20).mean()
    vol_score = 1 if val(volume.iloc[-1]) > val(vol_ma.iloc[-1]) else 0

    return (trend + momentum + vol_score) / 3

# ================= SIZE =================
def position_size(price, atr_val):
    if atr_val == 0 or np.isnan(atr_val):
        return 0
    risk = ACCOUNT * RISK_PER_TRADE
    return round(risk / atr_val, 2)

print("🚀 ADAPTIVE QUANT ENGINE STARTED")

while True:
    now = datetime.now()
    regime = detect_regime()
    params = get_params(regime)

    print(f"\n⏱ {now} | REGIME: {regime}")

    for symbol in SYMBOLS:

        df = get_data(symbol)
        if df is None:
            continue

        price = val(df["Close"].iloc[-1])
        atr_val = atr(df)

        if atr_val == 0 or np.isnan(atr_val):
            continue

        atr_pct = atr_val / price
        tp_pct = (atr_val * params["tp_mult"]) / price

        # FILTER
        if atr_pct < params["min_atr_pct"]:
            continue
        if tp_pct < params["min_tp_pct"]:
            continue

        # ENTRY
        if symbol not in positions and len(positions) < params["max_positions"]:
            score = signal_score(df)

            if score >= 0.66:
                size = position_size(price, atr_val)
                if size <= 0:
                    continue

                sl = price - atr_val * params["sl_mult"]
                tp = price + atr_val * params["tp_mult"]

                positions[symbol] = {
                    "entry": price,
                    "size": size,
                    "sl": sl,
                    "tp": tp,
                    "max_price": price
                }

                print(f"🚀 LONG {symbol} | {price:.2f} | SL:{sl:.2f} TP:{tp:.2f} | score:{score:.2f}")

        # MANAGEMENT
        elif symbol in positions:
            pos = positions[symbol]

            pnl = (price - pos["entry"]) * pos["size"]

            pos["max_price"] = max(pos["max_price"], price)
            trailing_sl = pos["max_price"] - atr_val

            if price <= pos["sl"]:
                reason = "SL"
            elif price >= pos["tp"]:
                reason = "TP"
            elif price <= trailing_sl:
                reason = "TRAIL"
            else:
                continue

            print(f"❌ EXIT {symbol} | {reason} | PnL:{pnl:.2f}")

            del positions[symbol]

    time.sleep(SCAN_INTERVAL)