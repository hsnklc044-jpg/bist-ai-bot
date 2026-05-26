# =========================================
# FILE: v1106_ULTRA_PRO_ENGINE_ELITE.py
# =========================================

import yfinance as yf
import pandas as pd
import numpy as np
import time
import json
import sys
import os
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

ACCOUNT = 10000
RISK_PER_TRADE = 0.02
ATR_PERIOD = 14
SCAN_INTERVAL = 10
MAX_TRADES = 2
MAX_HOLD = 300  # saniye

positions = {}
trade_log = []

# ================= SILENT =================
class suppress_output:
    def __enter__(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self._stdout
        sys.stderr = self._stderr

def safe_download(symbol):
    try:
        with suppress_output():
            return yf.download(symbol, period="1d", interval="1m", progress=False)
    except:
        return None

def val(x):
    try:
        return float(x.iloc[0]) if hasattr(x, "iloc") else float(x)
    except:
        return np.nan

# ================= ATR =================
def calculate_atr(df):
    df = df.copy()
    df["H-L"] = df["High"] - df["Low"]
    df["H-C"] = (df["High"] - df["Close"].shift()).abs()
    df["L-C"] = (df["Low"] - df["Close"].shift()).abs()
    tr = df[["H-L", "H-C", "L-C"]].max(axis=1)
    atr = tr.rolling(ATR_PERIOD).mean()
    return val(atr.iloc[-1])

# ================= SIGNAL =================
def generate_signal(df):
    ma = df["Close"].rolling(20).mean()

    ma_val = val(ma.iloc[-1])
    close_val = val(df["Close"].iloc[-1])
    prev_val = val(df["Close"].iloc[-5])

    if np.isnan(ma_val) or np.isnan(close_val) or np.isnan(prev_val):
        return None, 0

    momentum = close_val - prev_val

    score = 0
    if close_val > ma_val:
        score += 0.5
    if momentum > 0:
        score += 0.5

    return ("LONG", score) if score >= 0.5 else (None, score)

# ================= SIZE =================
def position_size(price, atr):
    if atr == 0 or np.isnan(atr):
        return 0

    risk_amount = ACCOUNT * RISK_PER_TRADE
    raw_size = risk_amount / atr

    max_value = ACCOUNT * 0.20
    max_size = max_value / price

    size = min(raw_size, max_size)

    if size * price < 500:
        return 0

    return round(size, 2)

# ================= SAVE =================
def save_dashboard():
    with open("live_positions.json", "w") as f:
        json.dump(positions, f, indent=2)

    if trade_log:
        pd.DataFrame(trade_log).to_csv("trade_log.csv", index=False)

# ================= ENGINE =================
print("🚀 ELITE ENGINE STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    candidates = []

    # SIGNAL TOPLA
    for symbol in SYMBOLS:
        df = safe_download(symbol)
        if df is None or df.empty or len(df) < 50:
            continue

        price = val(df["Close"].iloc[-1])
        atr = calculate_atr(df)

        side, score = generate_signal(df)

        if side:
            candidates.append({
                "symbol": symbol,
                "price": price,
                "atr": atr,
                "score": score
            })

    # EN İYİLER
    candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)
    selected = candidates[:MAX_TRADES]

    # ENTRY
    for c in selected:
        symbol = c["symbol"]

        if symbol in positions:
            continue

        size = position_size(c["price"], c["atr"])
        if size <= 0:
            continue

        positions[symbol] = {
            "entry": c["price"],
            "atr": c["atr"],
            "size": size,
            "time": time.time(),
            "max_price": c["price"]
        }

        print(f"🚀 LONG {symbol} | {c['price']:.2f} size:{size}")

    # EXIT + MANAGEMENT
    for symbol in list(positions.keys()):
        df = safe_download(symbol)
        if df is None or df.empty:
            continue

        price = val(df["Close"].iloc[-1])
        pos = positions[symbol]

        entry = pos["entry"]
        size = pos["size"]
        atr = pos["atr"]

        pnl = (price - entry) * size

        # 🔥 max price update
        pos["max_price"] = max(pos["max_price"], price)

        # 🔥 trailing stop
        trailing_sl = pos["max_price"] - atr

        # 🔥 breakeven
        if price > entry + atr:
            breakeven = entry
        else:
            breakeven = -999

        # 🔥 time exit
        if time.time() - pos["time"] > MAX_HOLD:
            reason = "TIME"
        elif price < trailing_sl:
            reason = "TRAIL"
        elif price < breakeven:
            reason = "BE"
        else:
            continue

        print(f"❌ EXIT {symbol} | PnL:{pnl:.2f} {reason}")

        trade_log.append({
            "time": str(now),
            "symbol": symbol,
            "pnl": pnl,
            "reason": reason
        })

        del positions[symbol]

    save_dashboard()
    time.sleep(SCAN_INTERVAL)