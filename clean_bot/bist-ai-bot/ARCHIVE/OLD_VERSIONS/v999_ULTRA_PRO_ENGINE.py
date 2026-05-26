import yfinance as yf
import pandas as pd
import numpy as np
import time, os, csv, json, requests
from datetime import datetime

# ================= CONFIG =================
SYMBOLS = ["TUPRS.IS","EREGL.IS","SISE.IS","BTC-USD","ETH-USD"]
TF = "5m"
LOOKBACK = 10

ACCOUNT = 100000
BASE_RISK = 0.01
MAX_RISK = 0.03
MAX_POS = 2

ATR_SL = 0.8
ATR_TP = 2.0
MAX_TIME = 600

LOG_FILE = "trades_log.csv"
POS_FILE = "positions.json"

# ===== TELEGRAM =====
TOKEN = "BURAYA_BOT_TOKEN"
CHAT_ID = "BURAYA_CHAT_ID"

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# ================= STORAGE =================
positions = {}

def save_pos():
    with open(POS_FILE,"w") as f:
        json.dump(positions,f,default=str)

def log(row):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE,"a",newline="",encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(["time","symbol","side","entry","exit","pnl","reason"])
        w.writerow(row)

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

# ================= SIGNAL =================
def signal(df):
    c,h,l = df.iloc[-1][["Close","High","Low"]]
    r = (h-l)+1e-9
    buy = (c-l)/r
    sell = (h-c)/r

    if buy > 0.3:
        return "LONG", buy
    elif sell > 0.3:
        return "SHORT", sell
    return None, 0

# ================= SIZE =================
def size(price, conf):
    risk = BASE_RISK + (MAX_RISK-BASE_RISK)*conf
    return round((ACCOUNT*risk)/price,4)

# ================= ENGINE =================
print("🚀 ULTRA PRO ENGINE STARTED")

while True:
    try:
        print("\n⏱", datetime.now())

        # ===== ENTRY =====
        for sym in SYMBOLS:
            if len(positions) >= MAX_POS:
                break
            if sym in positions:
                continue

            df = get(sym)
            if df is None or len(df) < 50:
                continue

            df["ATR"] = atr(df)
            side, conf = signal(df)

            if not side:
                continue

            price = df["Close"].iloc[-1]
            atr_v = df["ATR"].iloc[-1]
            qty = size(price, conf)

            positions[sym] = {
                "side": side,
                "entry": price,
                "atr": atr_v,
                "size": qty,
                "time": datetime.now(),
                "max": price,
                "min": price,
                "partial": False
            }

            msg = f"🚀 {side} {sym}\nPrice:{price:.2f}\nSize:{qty}"
            print(msg)
            send(msg)

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

            p["max"] = max(p["max"], price)
            p["min"] = min(p["min"], price)

            pnl = (price-entry)*qty if side=="LONG" else (entry-price)*qty

            sl = atr_v*ATR_SL
            tp = atr_v*ATR_TP

            exit = False
            reason = ""

            if side=="LONG":
                if price <= entry-sl:
                    exit=True; reason="SL"
                if price >= entry+tp and not p["partial"]:
                    close_qty = qty*0.5
                    pnl_part = (price-entry)*close_qty
                    p["size"] -= close_qty
                    p["partial"]=True
                    print(f"💰 PARTIAL {sym} {pnl_part:.2f}")
                trail = p["max"] - atr_v*0.8
                if price <= trail:
                    exit=True; reason="TRAIL"

            else:
                if price >= entry+sl:
                    exit=True; reason="SL"
                if price <= entry-tp and not p["partial"]:
                    close_qty = qty*0.5
                    pnl_part = (entry-price)*close_qty
                    p["size"] -= close_qty
                    p["partial"]=True
                    print(f"💰 PARTIAL {sym} {pnl_part:.2f}")
                trail = p["min"] + atr_v*0.8
                if price >= trail:
                    exit=True; reason="TRAIL"

            if (datetime.now()-p["time"]).seconds > MAX_TIME:
                exit=True; reason="TIME"

            if exit:
                msg = f"❌ EXIT {sym}\nPnL:{pnl:.2f}\nReason:{reason}"
                print(msg)
                send(msg)

                log([datetime.now(), sym, side, entry, price, pnl, reason])
                del positions[sym]

        save_pos()

    except Exception as e:
        print("ERROR:", e)

    time.sleep(10)