# =========================================
# FILE: v1108_ULTRA_PRO_ENGINE_FINAL_RISK.py
# =========================================

import yfinance as yf
import pandas as pd
import numpy as np
import time
import json
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

ACCOUNT = 10000
RISK_PER_TRADE = 0.01   # 🔥 %1 risk (pro seviye)
MAX_POSITION_PCT = 0.10 # 🔥 max %10 sermaye
ATR_PERIOD = 14
SCAN_INTERVAL = 5
MAX_TRADES = 2

positions = {}
trade_log = []

def val(x):
    try:
        return float(x.iloc[0]) if hasattr(x, "iloc") else float(x)
    except:
        return np.nan

def get_data(symbol):
    try:
        return yf.download(symbol, period="1d", interval="1m", progress=False)
    except:
        return None

def calculate_atr(df):
    df["tr"] = np.maximum(df["High"] - df["Low"],
                          np.maximum(abs(df["High"] - df["Close"].shift()),
                                     abs(df["Low"] - df["Close"].shift())))
    return val(df["tr"].rolling(ATR_PERIOD).mean().iloc[-1])

def generate_signal(df):
    ma = df["Close"].rolling(20).mean()
    close = val(df["Close"].iloc[-1])
    ma_val = val(ma.iloc[-1])
    momentum = close - val(df["Close"].iloc[-5])

    score = 0
    if close > ma_val: score += 0.5
    if momentum > 0: score += 0.5

    return ("LONG", score) if score >= 0.5 else (None, score)

# 🔥 PROFESYONEL SIZE
def position_size(price, atr):
    if atr == 0 or np.isnan(atr):
        return 0

    # risk bazlı size
    risk_amount = ACCOUNT * RISK_PER_TRADE
    size_risk = risk_amount / atr

    # portföy limiti
    max_value = ACCOUNT * MAX_POSITION_PCT
    size_cap = max_value / price

    # final size
    size = min(size_risk, size_cap)

    return round(size, 2)

def save():
    with open("live_positions.json", "w") as f:
        json.dump(positions, f, indent=2)

    if trade_log:
        pd.DataFrame(trade_log).to_csv("trade_log.csv", index=False)

print("🚀 FINAL PRO RISK ENGINE STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    signals = []

    for s in SYMBOLS:
        df = get_data(s)
        if df is None or df.empty or len(df) < 50:
            continue

        price = val(df["Close"].iloc[-1])
        atr = calculate_atr(df)
        side, score = generate_signal(df)

        if side:
            signals.append((s, price, atr, score))

    signals = sorted(signals, key=lambda x: x[3], reverse=True)[:MAX_TRADES]

    # ENTRY
    for s, price, atr, score in signals:
        if s in positions:
            continue

        size = position_size(price, atr)

        if size <= 0:
            continue

        positions[s] = {
            "entry": price,
            "atr": atr,
            "size": size,
            "max_price": price,
            "partial": False
        }

        print(f"🚀 LONG {s} | {price:.2f} size:{size} score:{score:.2f}")

    # MANAGEMENT
    for s in list(positions.keys()):
        df = get_data(s)
        if df is None or df.empty:
            continue

        price = val(df["Close"].iloc[-1])
        pos = positions[s]

        pnl = (price - pos["entry"]) * pos["size"]
        pos["max_price"] = max(pos["max_price"], price)

        atr = pos["atr"]

        # partial
        if not pos["partial"] and pnl > atr * pos["size"]:
            pos["size"] *= 0.5
            pos["partial"] = True
            print(f"💰 PARTIAL {s} | PnL:{pnl:.2f}")

        trailing = pos["max_price"] - atr * 0.5
        sl = pos["entry"] - atr
        tp = pos["entry"] + atr * 2

        if price < trailing or price < sl or price > tp:
            result = "WIN" if pnl > 0 else "LOSS"

            print(f"❌ EXIT {s} | PnL:{pnl:.2f} {result}")

            trade_log.append({
                "time": str(now),
                "symbol": s,
                "pnl": pnl,
                "result": result
            })

            del positions[s]

    save()
    time.sleep(SCAN_INTERVAL)