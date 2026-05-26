# =========================================
# FILE: v1116_ULTRA_PRO_ENGINE_PRO_FILTERED.py
# =========================================

import yfinance as yf
import numpy as np
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

ACCOUNT = 10000
RISK_PER_TRADE = 0.01
ATR_PERIOD = 14
SCAN_INTERVAL = 5

MIN_ATR_PCT = 0.002   # %0.2 altı trade yok
MIN_TP_PCT = 0.005    # %0.5 altı TP yok

positions = {}

def val(x):
    try:
        return float(x.iloc[0]) if hasattr(x, "iloc") else float(x)
    except:
        return np.nan

def get_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False)
        return df if df is not None and not df.empty else None
    except:
        return None

def atr(df):
    tr = np.maximum(df["High"] - df["Low"],
                    np.maximum(abs(df["High"] - df["Close"].shift()),
                               abs(df["Low"] - df["Close"].shift())))
    return val(tr.rolling(ATR_PERIOD).mean().iloc[-1])

def signal(df):
    ma = df["Close"].rolling(20).mean()
    return "LONG" if val(df["Close"].iloc[-1]) > val(ma.iloc[-1]) else None

def position_size(price, atr_val):
    risk = ACCOUNT * RISK_PER_TRADE
    return round(risk / atr_val, 2)

print("🚀 PRO FILTERED ENGINE STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    for symbol in SYMBOLS:
        df = get_data(symbol)
        if df is None:
            continue

        price = val(df["Close"].iloc[-1])
        atr_val = atr(df)

        # ================= FILTER =================
        atr_pct = atr_val / price

        if atr_pct < MIN_ATR_PCT:
            continue

        tp_pct = (atr_val * 3) / price

        if tp_pct < MIN_TP_PCT:
            continue

        # ================= ENTRY =================
        if symbol not in positions:
            if signal(df):
                size = position_size(price, atr_val)

                sl = price - atr_val
                tp = price + atr_val * 3

                positions[symbol] = {
                    "entry": price,
                    "size": size,
                    "sl": sl,
                    "tp": tp,
                    "max_price": price
                }

                print(f"🚀 LONG {symbol} | {price:.2f} | SL:{sl:.2f} TP:{tp:.2f}")

        # ================= MANAGEMENT =================
        else:
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