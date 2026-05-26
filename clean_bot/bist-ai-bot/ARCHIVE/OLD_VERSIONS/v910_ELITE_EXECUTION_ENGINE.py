import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime

# ================= CONFIG =================
SYMBOLS = [
    "TUPRS.IS","EREGL.IS","SISE.IS",
    "BTC-USD","ETH-USD",
    "EURUSD=X","GBPUSD=X"
]

TF = "5m"
LOOKBACK = 30

ACCOUNT_SIZE = 100000
BASE_RISK = 0.01
MAX_RISK = 0.03

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

# ================= INDICATORS =================
def atr(df):
    tr = pd.concat([
        df['High']-df['Low'],
        (df['High']-df['Close'].shift()).abs(),
        (df['Low']-df['Close'].shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(14).mean()

def regime(df, sym):
    ma = df["Close"].rolling(50).mean()
    vol = df["Close"].pct_change().rolling(20).std()

    vol_th = 0.003 if "USD" in sym else 0.001

    trend = abs(df["Close"].iloc[-1] - ma.iloc[-1]) / ma.iloc[-1] > 0.002
    volatility = vol.iloc[-1] > vol_th

    return trend and volatility

# ================= SIGNAL =================
def signal(df):
    last = df.iloc[-1]
    c,h,l = last["Close"], last["High"], last["Low"]

    rng = (h-l)+1e-9
    buy = (c-l)/rng
    sell = (h-c)/rng

    if buy > 0.3:
        return "LONG", buy
    elif sell > 0.3:
        return "SHORT", sell
    return None, 0

# ================= RISK =================
def position_size(price, confidence):
    risk = BASE_RISK + (MAX_RISK - BASE_RISK) * confidence
    return round((ACCOUNT_SIZE * risk) / price, 4)

# ================= MAIN =================
print("🚀 ELITE EXECUTION ENGINE STARTED")

while True:
    try:
        print("\n⏱", datetime.now())

        # ===== ENTRY =====
        for sym in SYMBOLS:

            if len(positions) >= MAX_POSITIONS:
                break

            if sym in positions:
                continue

            df = get(sym)
            if df is None or len(df) < 50:
                continue

            df["ATR"] = atr(df)

            if not regime(df, sym):
                continue

            side, conf = signal(df)
            if not side:
                continue

            price = df["Close"].iloc[-1]
            atr_v = df["ATR"].iloc[-1]

            size = position_size(price, conf)

            positions[sym] = {
                "side": side,
                "entry": price,
                "atr": atr_v,
                "size": size,
                "time": datetime.now(),
                "max_price": price,
                "min_price": price,
                "partial_done": False
            }

            print(f"🚀 {side} {sym} | price:{price:.2f} size:{size} conf:{conf:.2f}")

        # ===== EXIT =====
        for sym in list(positions.keys()):
            df = get(sym)
            if df is None:
                continue

            pos = positions[sym]
            price = df["Close"].iloc[-1]

            entry = pos["entry"]
            atr_v = pos["atr"]
            size = pos["size"]
            side = pos["side"]

            # update extremes
            pos["max_price"] = max(pos["max_price"], price)
            pos["min_price"] = min(pos["min_price"], price)

            pnl = (price-entry)*size if side=="LONG" else (entry-price)*size

            sl = atr_v * ATR_SL
            tp = atr_v * ATR_TP

            exit_flag = False
            reason = ""

            # ===== LONG =====
            if side == "LONG":

                if price <= entry - sl:
                    reason="SL"; exit_flag=True

                elif price >= entry + sl:
                    pos["be"] = True

                # 🔥 PARTIAL TP (%50)
                if not pos["partial_done"] and price >= entry + tp:
                    close_size = size * 0.5
                    pnl_part = (price-entry) * close_size
                    pos["size"] -= close_size
                    pos["partial_done"] = True
                    print(f"💰 PARTIAL {sym} +{pnl_part:.2f}")

                # 🔥 TRAILING
                if "be" in pos:
                    trail = pos["max_price"] - atr_v * 0.8
                    if price <= trail:
                        reason="TRAIL"; exit_flag=True

            # ===== SHORT =====
            else:

                if price >= entry + sl:
                    reason="SL"; exit_flag=True

                elif price <= entry - sl:
                    pos["be"] = True

                if not pos["partial_done"] and price <= entry - tp:
                    close_size = size * 0.5
                    pnl_part = (entry-price) * close_size
                    pos["size"] -= close_size
                    pos["partial_done"] = True
                    print(f"💰 PARTIAL {sym} +{pnl_part:.2f}")

                if "be" in pos:
                    trail = pos["min_price"] + atr_v * 0.8
                    if price >= trail:
                        reason="TRAIL"; exit_flag=True

            # TIME EXIT
            if (datetime.now() - pos["time"]).seconds > MAX_DURATION:
                reason="TIME"; exit_flag=True

            if exit_flag:
                print(f"❌ EXIT {sym} {reason} PnL:{pnl:.2f}")
                del positions[sym]

    except Exception as e:
        print("ERROR:", e)

    time.sleep(10)