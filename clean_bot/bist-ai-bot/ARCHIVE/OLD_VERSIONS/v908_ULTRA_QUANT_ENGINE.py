import yfinance as yf
import pandas as pd
import numpy as np
import json, time
from datetime import datetime

# ================= CONFIG =================
SYMBOLS = [
    "TUPRS.IS","EREGL.IS","SISE.IS",
    "BTC-USD","ETH-USD",
    "EURUSD=X","GBPUSD=X"
]

TF = "5m"
LOOKBACK = 30

ATR_SL = 0.8
ATR_TP = 2.0
MAX_DURATION = 1200

MAX_POSITIONS = 2

positions = {}

# ================= DATA =================
def get(sym):
    df = yf.download(sym, period=f"{LOOKBACK}d", interval=TF, progress=False)
    if df is None or df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna()

# ================= ATR =================
def atr(df):
    tr = pd.concat([
        df['High']-df['Low'],
        (df['High']-df['Close'].shift()).abs(),
        (df['Low']-df['Close'].shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(14).mean()

# ================= REGIME =================
def regime(df):
    ma = df["Close"].rolling(50).mean()
    vol = df["Close"].pct_change().rolling(20).std()

    trend = df["Close"].iloc[-1] > ma.iloc[-1]
    volatility = vol.iloc[-1] > 0.002

    return trend and volatility

# ================= SIGNAL =================
def signal(df):
    last = df.iloc[-1]
    c,h,l = last["Close"], last["High"], last["Low"]

    rng = (h-l)+1e-9
    if (c-l)/rng > 0.3:
        return "LONG"
    elif (h-c)/rng > 0.3:
        return "SHORT"
    return None

# ================= MAIN =================
print("🚀 ULTRA QUANT ENGINE STARTED")

while True:
    try:
        print("\n⏱", datetime.now())

        for sym in SYMBOLS:

            if len(positions) >= MAX_POSITIONS:
                break

            df = get(sym)
            if df is None or len(df) < 50:
                continue

            df["ATR"] = atr(df)

            # 🔥 REGIME FILTER
            if not regime(df):
                continue

            sig = signal(df)
            if not sig:
                continue

            price = df["Close"].iloc[-1]
            atr_v = df["ATR"].iloc[-1]

            # ENTRY
            if sym not in positions:
                positions[sym] = {
                    "side": sig,
                    "entry": price,
                    "atr": atr_v,
                    "time": datetime.now()
                }

                print(f"🚀 {sig} {sym} {price}")

        # EXIT
        for sym in list(positions.keys()):
            df = get(sym)
            if df is None:
                continue

            pos = positions[sym]
            price = df["Close"].iloc[-1]

            entry = pos["entry"]
            atr_v = pos["atr"]
            side = pos["side"]

            pnl = (price-entry) if side=="LONG" else (entry-price)

            sl = atr_v * ATR_SL
            tp = atr_v * ATR_TP

            exit_flag = False

            if side=="LONG":
                if price <= entry-sl:
                    exit_flag=True
                elif price >= entry+tp:
                    exit_flag=True
            else:
                if price >= entry+sl:
                    exit_flag=True
                elif price <= entry-tp:
                    exit_flag=True

            if (datetime.now() - pos["time"]).seconds > MAX_DURATION:
                exit_flag=True

            if exit_flag:
                print(f"❌ EXIT {sym} PnL:{pnl:.2f}")
                del positions[sym]

    except Exception as e:
        print("ERROR:", e)

    time.sleep(10)