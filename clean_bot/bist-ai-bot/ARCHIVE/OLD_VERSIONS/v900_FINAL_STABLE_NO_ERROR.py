import yfinance as yf
import requests
import time as tm   # 🔥 KRİTİK FIX
import pandas as pd
from datetime import datetime
import csv, os

TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

SYMBOLS = ["TUPRS.IS","EREGL.IS","SISE.IS"]

SCAN_SLEEP = 3

ACCOUNT_SIZE = 100000
RISK_PER_TRADE = 0.02

SL_ATR = 1.0
TP_ATR = 2.0
TRAIL_ATR = 0.8

positions = {}
total_pnl = 0

# ================= TELEGRAM =================
def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=5)
    except:
        pass

# ================= INDICATORS =================
def rsi(df):
    d = df['Close'].diff()
    gain = d.clip(lower=0).rolling(14).mean()
    loss = (-d.clip(upper=0)).rolling(14).mean()
    rs = gain/loss
    return 100 - (100/(1+rs))

def atr(df):
    tr = pd.concat([
        df['High']-df['Low'],
        (df['High']-df['Close'].shift()).abs(),
        (df['Low']-df['Close'].shift()).abs()
    ],axis=1).max(axis=1)
    return tr.rolling(14).mean()

# ================= DATA =================
def get(sym):
    try:
        df = yf.download(sym, interval="1m", period="1d", progress=False)
        if df is None or df.empty or len(df)<50:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return None

# ================= SIGNAL =================
def analyze(df):
    df['rsi'] = rsi(df)
    df['atr'] = atr(df)

    last = df.iloc[-1]

    r = float(last['rsi'])
    c = float(last['Close'])
    h = float(last['High'])
    l = float(last['Low'])

    rng = (h-l)+1e-9

    buy = (c-l)/rng
    sell = (h-c)/rng

    if buy > 0.3 and r < 50:
        return "LONG", c, float(last['atr'])

    if sell > 0.3 and r > 50:
        return "SHORT", c, float(last['atr'])

    return None, None, None

# ================= MAIN =================
print("🚀 FINAL SYSTEM STARTED")
send("🚀 FINAL SYSTEM STARTED")

while True:
    try:
        for sym in SYMBOLS:

            df = get(sym)
            if df is None:
                continue

            side, price, atr_v = analyze(df)
            if side is None:
                continue

            # ================= EXIT =================
            if sym in positions:
                pos = positions[sym]

                entry = pos["entry"]
                trail = pos["trail"]

                exit_signal = False

                if pos["side"] == "LONG":

                    trail = max(trail, price)
                    pos["trail"] = trail

                    if price <= entry - SL_ATR*atr_v:
                        reason="SL"; exit_signal=True
                    elif price >= entry + TP_ATR*atr_v:
                        reason="TP"; exit_signal=True
                    elif price <= trail - TRAIL_ATR*atr_v:
                        reason="TRAIL"; exit_signal=True
                    elif side == "SHORT":
                        reason="REV"; exit_signal=True

                    if exit_signal:
                        pnl = (price-entry)*pos["size"]

                else:

                    trail = min(trail, price)
                    pos["trail"] = trail

                    if price >= entry + SL_ATR*atr_v:
                        reason="SL"; exit_signal=True
                    elif price <= entry - TP_ATR*atr_v:
                        reason="TP"; exit_signal=True
                    elif price >= trail + TRAIL_ATR*atr_v:
                        reason="TRAIL"; exit_signal=True
                    elif side == "LONG":
                        reason="REV"; exit_signal=True

                    if exit_signal:
                        pnl = (entry-price)*pos["size"]

                if exit_signal:
                    print(f"❌ EXIT {sym} {reason} {pnl:.2f}")
                    total_pnl += pnl
                    del positions[sym]
                    continue

                continue

            # ================= ENTRY =================
            size = round((ACCOUNT_SIZE*RISK_PER_TRADE)/(atr_v*price),2)

            positions[sym] = {
                "side": side,
                "entry": price,
                "size": size,
                "trail": price
            }

            msg = f"{side} {sym}\nPrice:{price}\nSize:{size}\nPnL:{total_pnl:.2f}"
            print(msg)
            send(msg)

        tm.sleep(SCAN_SLEEP)

    except Exception as e:
        print("❌ ERROR:", e)
        tm.sleep(SCAN_SLEEP)