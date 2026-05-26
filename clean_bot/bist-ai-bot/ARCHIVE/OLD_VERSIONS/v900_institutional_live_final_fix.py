import yfinance as yf
import requests
import time as tm
import pandas as pd
from datetime import datetime
import csv, os

# ================== CONFIG ==================
TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

SYMBOLS = ["TUPRS.IS","EREGL.IS","SISE.IS"]

SCAN_SLEEP = 3

ACCOUNT_SIZE = 100000
RISK_PER_TRADE = 0.02
MAX_TOTAL_RISK = 0.05

SL_ATR = 1.0
TP_ATR = 2.0
TRAIL_ATR = 0.8

LOG_FILE = "trades.csv"

positions = {}
total_pnl = 0

# ================== TELEGRAM ==================
def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=5)
    except:
        pass

# ================== LOG ==================
def log(row):
    f = os.path.isfile(LOG_FILE)
    with open(LOG_FILE,"a",newline="",encoding="utf-8") as file:
        w = csv.writer(file)
        if not f:
            w.writerow(["time","symbol","side","entry","exit","pnl"])
        w.writerow(row)

# ================== INDICATORS ==================
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

# ================== DATA ==================
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

# ================== ANALYZE ==================
def analyze(sym, df):
    df['rsi'] = rsi(df)
    df['atr'] = atr(df)

    last = df.iloc[-1]

    r = float(last['rsi'])
    c = float(last['Close'])
    h = float(last['High'])
    l = float(last['Low'])

    rng = (h-l)+1e-9
    buy_w = (c-l)/rng
    sell_w = (h-c)/rng

    score_buy = (buy_w>0.3)*2 + (r<50)
    score_sell = (sell_w>0.3)*2 + (r>50)

    if score_buy > score_sell and score_buy>=2:
        return {"side":"LONG","price":c,"atr":float(last['atr']),"score":score_buy}
    elif score_sell>=2:
        return {"side":"SHORT","price":c,"atr":float(last['atr']),"score":score_sell}

    return None

# ================== MAIN ==================
print("🚀 SYSTEM STARTED")
send("🧠 SYSTEM STARTED")

while True:
    try:
        for sym in SYMBOLS:
            df = get(sym)
            if df is None:
                continue

            sig = analyze(sym, df)
            if sig is None:
                continue

            price = sig["price"]
            atr_v = sig["atr"]

            # ================== EXIT ==================
            if sym in positions:
                pos = positions[sym]
                entry = pos["entry"]
                side = pos["side"]

                pos["trail"] = pos.get("trail", entry)

                exit_signal = False

                if side == "LONG":
                    pos["trail"] = max(pos["trail"], price)

                    if price <= entry - SL_ATR*atr_v:
                        reason="SL"; exit_signal=True
                    elif price >= entry + TP_ATR*atr_v:
                        reason="TP"; exit_signal=True
                    elif price <= pos["trail"] - TRAIL_ATR*atr_v:
                        reason="TRAIL"; exit_signal=True
                    elif sig and sig["side"]=="SHORT":
                        reason="REVERSAL"; exit_signal=True

                    if exit_signal:
                        pnl = (price-entry)*pos["size"]

                else:
                    pos["trail"] = min(pos["trail"], price)

                    if price >= entry + SL_ATR*atr_v:
                        reason="SL"; exit_signal=True
                    elif price <= entry - TP_ATR*atr_v:
                        reason="TP"; exit_signal=True
                    elif price >= pos["trail"] + TRAIL_ATR*atr_v:
                        reason="TRAIL"; exit_signal=True
                    elif sig and sig["side"]=="LONG":
                        reason="REVERSAL"; exit_signal=True

                    if exit_signal:
                        pnl = (entry-price)*pos["size"]

                if exit_signal:
                    print(f"❌ EXIT {sym} {reason} {pnl:.2f}")
                    total_pnl += pnl
                    log([datetime.now(),sym,side,entry,price,pnl])
                    del positions[sym]
                    continue

                continue

            # ================== ENTRY ==================
            if len(positions) >= 3:
                continue

            size = round((ACCOUNT_SIZE*RISK_PER_TRADE)/(atr_v*price),2)

            positions[sym] = {
                "side": sig["side"],
                "entry": price,
                "size": size,
                "trail": price
            }

            msg = f"{sig['side']} {sym}\nPrice:{price}\nSize:{size}\nPnL:{total_pnl:.2f}"
            print("🚀", msg)
            send(msg)

        tm.sleep(SCAN_SLEEP)

    except Exception as e:
        print("❌ hata:", e)
        tm.sleep(SCAN_SLEEP)