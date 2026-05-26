# =========================================
# FILE: v1104_ULTRA_PRO_ENGINE_TRUE_SILENT.py
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

positions = {}
trade_log = []

# ================= HARD SILENT =================
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

# ================= SAFE VALUE =================
def val(x):
    try:
        return float(x.iloc[0]) if hasattr(x, "iloc") else float(x)
    except:
        return np.nan

# ================= SAFE DOWNLOAD =================
def safe_download(symbol):
    try:
        with suppress_output():
            df = yf.download(symbol, period="1d", interval="1m", progress=False)
        return df
    except:
        return None

# ================= ATR =================
def calculate_atr(df):
    df = df.copy()

    df["H-L"] = df["High"] - df["Low"]
    df["H-C"] = (df["High"] - df["Close"].shift()).abs()
    df["L-C"] = (df["Low"] - df["Close"].shift()).abs()

    tr = df[["H-L", "H-C", "L-C"]].max(axis=1)
    atr = tr.rolling(ATR_PERIOD).mean()

    return val(atr.iloc[-1])

# ================= REGIME (TRUE SILENT) =================
def regime_filter():
    df = safe_download("^XU100")

    if df is None or df.empty or len(df) < 50:
        return True  # fallback

    ma = df["Close"].rolling(50).mean()
    vol = df["Close"].pct_change().rolling(20).std()

    ma_val = val(ma.iloc[-1])
    vol_val = val(vol.iloc[-1])
    close_val = val(df["Close"].iloc[-1])

    if np.isnan(ma_val) or np.isnan(vol_val):
        return True

    trend = close_val > ma_val * 0.998
    volatility = vol_val > 0.0005

    return trend or volatility

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

# ================= POSITION SIZE =================
def position_size(price, atr):

    if atr == 0 or np.isnan(atr):
        return 0

    risk_amount = ACCOUNT * RISK_PER_TRADE
    raw_size = risk_amount / atr

    max_position_value = ACCOUNT * 0.20
    max_size = max_position_value / price

    final_size = min(raw_size, max_size)

    if final_size * price < 500:
        return 0

    return round(final_size, 2)

# ================= SAVE =================
def save_dashboard():
    with open("live_positions.json", "w") as f:
        json.dump(positions, f, indent=2)

    if trade_log:
        pd.DataFrame(trade_log).to_csv("trade_log.csv", index=False)

# ================= ENGINE =================
print("🚀 ULTRA PRO ENGINE (TRUE SILENT) STARTED")

while True:
    now = datetime.now()
    print(f"\n⏱ {now}")

    market_ok = regime_filter()
    score_threshold = 0.75 if not market_ok else 0.5

    for symbol in SYMBOLS:
        df = safe_download(symbol)

        if df is None or df.empty or len(df) < 50:
            continue

        price = val(df["Close"].iloc[-1])
        atr = calculate_atr(df)

        if np.isnan(price) or np.isnan(atr):
            continue

        side, score = generate_signal(df)

        # ENTRY
        if symbol not in positions:

            if not side or score < score_threshold:
                continue

            size = position_size(price, atr)

            if size <= 0:
                continue

            positions[symbol] = {
                "side": side,
                "entry": price,
                "atr": atr,
                "size": size,
                "time": str(now),
                "max_price": price,
                "min_price": price
            }

            print(f"🚀 {side} {symbol} | {price:.2f} size:{size} score:{score:.2f}")

        # EXIT
        else:
            pos = positions[symbol]

            entry = pos["entry"]
            size = pos["size"]

            pnl = (price - entry) * size

            pos["max_price"] = max(pos["max_price"], price)
            pos["min_price"] = min(pos["min_price"], price)

            tp = pos["atr"] * size * 2
            sl = pos["atr"] * size

            if pnl > tp:
                result = "WIN"
            elif pnl < -sl:
                result = "LOSS"
            else:
                continue

            print(f"❌ EXIT {symbol} | PnL:{pnl:.2f} {result}")

            trade_log.append({
                "time": str(now),
                "symbol": symbol,
                "entry": entry,
                "exit": price,
                "pnl": pnl,
                "result": result
            })

            del positions[symbol]

    save_dashboard()
    time.sleep(SCAN_INTERVAL)