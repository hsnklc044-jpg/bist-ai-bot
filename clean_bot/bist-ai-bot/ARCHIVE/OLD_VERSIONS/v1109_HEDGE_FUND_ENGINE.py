# =========================================
# FILE: v1109_HEDGE_FUND_ENGINE.py
# =========================================

import yfinance as yf
import pandas as pd
import numpy as np
import time
import json
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

ACCOUNT = 10000
RISK_PER_TRADE = 0.01
MAX_POSITION_PCT = 0.10
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

# ================= MARKET REGIME =================
def market_trend():
    df = get_data("^XU100")
    if df is None or df.empty:
        return "NEUTRAL"

    ma = df["Close"].rolling(50).mean()
    close = val(df["Close"].iloc[-1])
    ma_val = val(ma.iloc[-1])

    if close > ma_val:
        return "BULL"
    elif close < ma_val:
        return "BEAR"
    return "NEUTRAL"

# ================= ATR =================
def calculate_atr(df):
    df["tr"] = np.maximum(df["High"] - df["Low"],
                          np.maximum(abs(df["High"] - df["Close"].shift()),
                                     abs(df["Low"] - df["Close"].shift())))
    return val(df["tr"].rolling(ATR_PERIOD).mean().iloc[-1])

# ================= SIGNAL =================
def generate_signal(df, regime):
    ma = df["Close"].rolling(20).mean()

    close = val(df["Close"].iloc[-1])
    ma_val = val(ma.iloc[-1])
    momentum = close - val(df["Close"].iloc[-5])

    if np.isnan(close) or np.isnan(ma_val):
        return None, 0

    score = 0
    side = None

    if close > ma_val and momentum > 0:
        side = "LONG"
        score = 1.0

    elif close < ma_val and momentum < 0:
        side = "SHORT"
        score = 1.0

    # 🔥 REGIME FILTER
    if regime == "BULL" and side == "SHORT":
        return None, 0
    if regime == "BEAR" and side == "LONG":
        return None, 0

    return side, score

# ================= SIZE =================
def position_size(price, atr):
    if atr == 0 or np.isnan(atr):
        return 0

    risk_amount = ACCOUNT * RISK_PER_TRADE
    size_risk = risk_amount / atr

    max_value = ACCOUNT * MAX_POSITION_PCT
    size_cap = max_value / price

    return round(min(size_risk, size_cap), 2)

# ================= SAVE =================
def save():
    with open("live_positions.json", "w") as f:
        json.dump(positions, f, indent=2)

    if trade_log:
        pd.DataFrame(trade_log).to_csv("trade_log.csv", index=False)

print("🚀 HEDGE FUND ENGINE STARTED")

while True:
    now = datetime.now()
    regime = market_trend()

    print(f"\n⏱ {now} | MARKET: {regime}")

    signals = []

    for s in SYMBOLS:
        df = get_data(s)
        if df is None or df.empty or len(df) < 50:
            continue

        price = val(df["Close"].iloc[-1])
        atr = calculate_atr(df)

        side, score = generate_signal(df, regime)

        if side:
            signals.append((s, price, atr, score, side))

    signals = sorted(signals, key=lambda x: x[3], reverse=True)[:MAX_TRADES]

    # ENTRY
    for s, price, atr, score, side in signals:
        if s in positions:
            continue

        size = position_size(price, atr)
        if size <= 0:
            continue

        positions[s] = {
            "side": side,
            "entry": price,
            "atr": atr,
            "size": size,
            "max_price": price,
            "min_price": price,
            "partial": False
        }

        print(f"🚀 {side} {s} | {price:.2f} size:{size}")

    # MANAGEMENT
    for s in list(positions.keys()):
        df = get_data(s)
        if df is None or df.empty:
            continue

        price = val(df["Close"].iloc[-1])
        pos = positions[s]

        side = pos["side"]
        entry = pos["entry"]
        size = pos["size"]
        atr = pos["atr"]

        if side == "LONG":
            pnl = (price - entry) * size
            pos["max_price"] = max(pos["max_price"], price)
            trailing = pos["max_price"] - atr * 0.5
            exit_cond = price < trailing or price < entry - atr

        else:  # SHORT
            pnl = (entry - price) * size
            pos["min_price"] = min(pos["min_price"], price)
            trailing = pos["min_price"] + atr * 0.5
            exit_cond = price > trailing or price > entry + atr

        if exit_cond:
            result = "WIN" if pnl > 0 else "LOSS"

            print(f"❌ EXIT {s} | {side} PnL:{pnl:.2f} {result}")

            trade_log.append({
                "time": str(now),
                "symbol": s,
                "side": side,
                "pnl": pnl,
                "result": result
            })

            del positions[s]

    save()
    time.sleep(SCAN_INTERVAL)