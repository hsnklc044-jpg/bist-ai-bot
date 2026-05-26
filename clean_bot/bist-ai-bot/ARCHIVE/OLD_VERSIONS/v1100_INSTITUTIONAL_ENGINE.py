import yfinance as yf
import pandas as pd
import numpy as np
import time, json, os, csv
from datetime import datetime

# ================= CONFIG =================
SYMBOLS = ["TUPRS.IS","EREGL.IS","SISE.IS","BTC-USD","ETH-USD"]

TF = "5m"
LOOKBACK = 10

ACCOUNT = 100000
RISK_PER_TRADE = 0.01
MAX_PORTFOLIO_RISK = 0.03

ATR_SL = 1.0
ATR_TP = 2.2
MAX_TIME = 900

LOG_FILE = "trades_log.csv"
POS_FILE = "positions.json"

positions = {}

# ================= UTILS =================
def get(sym):
    try:
        df = yf.download(sym, period=f"{LOOKBACK}d", interval=TF, progress=False)
        if df is None or df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.dropna()
    except:
        return None

def atr(df):
    tr = pd.concat([
        df['High']-df['Low'],
        (df['High']-df['Close'].shift()).abs(),
        (df['Low']-df['Close'].shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(14).mean()

def log(row):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE,"a",newline="",encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(["time","symbol","side","entry","exit","pnl","reason"])
        w.writerow(row)

def save():
    with open(POS_FILE,"w") as f:
        json.dump(positions,f,default=str)

# ================= REGIME =================
def regime_filter():
    df = get("XU100.IS")
    if df is None:
        return False

    ma = df["Close"].rolling(50).mean()
    trend = df["Close"].iloc[-1] > ma.iloc[-1]

    vol = df["Close"].pct_change().rolling(20).std()
    volatility = vol.iloc[-1] > 0.001

    return trend and volatility

# ================= SIGNAL =================
def signal(df):
    c,h,l = df.iloc[-1][["Close","High","Low"]]
    r = (h-l)+1e-9

    momentum = (c - df["Close"].iloc[-5]) / df["Close"].iloc[-5]

    buy_score = (c-l)/r + momentum
    sell_score = (h-c)/r - momentum

    if buy_score > 0.6:
        return "LONG", buy_score
    elif sell_score > 0.6:
        return "SHORT", sell_score
    return None, 0

# ================= PORTFOLIO RISK =================
def current_risk():
    return len(positions) * RISK_PER_TRADE

def position_size(price):
    return round((ACCOUNT * RISK_PER_TRADE) / price, 4)

# ================= ENGINE =================
print("🚀 INSTITUTIONAL ENGINE STARTED")

while True:
    try:
        print("\n⏱", datetime.now())

        # ===== GLOBAL FILTER =====
        if not regime_filter():
            print("⛔ NO MARKET EDGE")
            time.sleep(10)
            continue

        # ===== ENTRY =====
        for sym in SYMBOLS:

            if sym in positions:
                continue

            if current_risk() >= MAX_PORTFOLIO_RISK:
                break

            df = get(sym)
            if df is None or len(df) < 50:
                continue

            df["ATR"] = atr(df)

            side, score = signal(df)

            if not side or score < 0.6:
                continue

            # Correlation protection
            same = [p for p in positions.values() if p["side"] == side]
            if len(same) >= 1:
                continue

            price = df["Close"].iloc[-1]
            atr_v = df["ATR"].iloc[-1]

            qty = position_size(price)

            positions[sym] = {
                "side": side,
                "entry": price,
                "atr": atr_v,
                "size": qty,
                "time": datetime.now(),
                "max": price,
                "min": price,
                "score": score
            }

            print(f"🚀 {side} {sym} | {price:.2f} | score:{score:.2f}")

        # ===== EXIT =====
        for sym in list(positions.keys()):
            df = get(sym)
            if df is None:
                continue

            p = positions[sym]
            price = df["Close"].iloc[-1]

            entry = p["entry"]
            atr_v = p["atr"]
            qty = p["size"]
            side = p["side"]

            pnl = (price-entry)*qty if side=="LONG" else (entry-price)*qty

            sl = atr_v * ATR_SL
            tp = atr_v * ATR_TP

            exit_flag = False
            reason = ""

            if side=="LONG":
                if price <= entry-sl:
                    exit_flag=True; reason="SL"
                elif price >= entry+tp:
                    exit_flag=True; reason="TP"

            else:
                if price >= entry+sl:
                    exit_flag=True; reason="SL"
                elif price <= entry-tp:
                    exit_flag=True; reason="TP"

            if (datetime.now()-p["time"]).seconds > MAX_TIME:
                exit_flag=True; reason="TIME"

            if exit_flag:
                print(f"❌ EXIT {sym} {reason} PnL:{pnl:.2f}")
                log([datetime.now(), sym, side, entry, price, pnl, reason])
                del positions[sym]

        save()

    except Exception as e:
        print("ERROR:", e)

    time.sleep(10)