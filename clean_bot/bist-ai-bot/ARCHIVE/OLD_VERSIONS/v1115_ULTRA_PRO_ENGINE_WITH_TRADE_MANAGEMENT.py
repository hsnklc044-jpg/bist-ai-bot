# =========================================
# FILE: v1115_ULTRA_PRO_ENGINE_WITH_TRADE_MANAGEMENT.py
# =========================================

import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

SCAN_INTERVAL = 5
ATR_PERIOD = 14
RISK_PER_TRADE = 0.01
ACCOUNT = 10000

positions = {}

# ================= SAFE VALUE =================
def val(x):
    try:
        return float(x.iloc[0]) if hasattr(x, "iloc") else float(x)
    except:
        return np.nan

# ================= DATA =================
def get_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False)
        return df if df is not None and not df.empty else None
    except:
        return None

# ================= ATR =================
def atr(df):
    df["tr"] = np.maximum(df["High"] - df["Low"],
                          np.maximum(abs(df["High"] - df["Close"].shift()),
                                     abs(df["Low"] - df["Close"].shift())))
    return val(df["tr"].rolling(ATR_PERIOD).mean().iloc[-1])

# ================= SIGNAL =================
def signal(df):
    close = df["Close"]
    ma = close.rolling(20).mean()

    if len(close) < 20:
        return None

    if val(close.iloc[-1]) > val(ma.iloc[-1]):
        return "LONG"

    return None

# ================= SIZE =================
def position_size(price, atr_val):
    if atr_val == 0 or np.isnan(atr_val):
        return 0
    risk = ACCOUNT * RISK_PER_TRADE
    return round(risk / atr_val, 2)

print("🚀 ENGINE WITH TRADE MANAGEMENT STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    for symbol in SYMBOLS:

        df = get_data(symbol)
        if df is None:
            continue

        price = val(df["Close"].iloc[-1])
        atr_val = atr(df)

        # ================= ENTRY =================
        if symbol not in positions:
            sig = signal(df)

            if sig:
                size = position_size(price, atr_val)
                if size <= 0:
                    continue

                sl = price - atr_val
                tp = price + atr_val * 2

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

            entry = pos["entry"]
            size = pos["size"]

            pnl = (price - entry) * size

            # trailing
            pos["max_price"] = max(pos["max_price"], price)
            trailing_sl = pos["max_price"] - atr_val

            # EXIT CONDITIONS
            if price <= pos["sl"]:
                result = "SL"
            elif price >= pos["tp"]:
                result = "TP"
            elif price <= trailing_sl:
                result = "TRAIL"
            else:
                continue

            print(f"❌ EXIT {symbol} | {result} | PnL:{pnl:.2f}")

            del positions[symbol]

    time.sleep(SCAN_INTERVAL)