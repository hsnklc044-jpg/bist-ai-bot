import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta

# ================= CONFIG =================
TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

SYMBOLS = ["TUPRS.IS","EREGL.IS","SISE.IS"]

INTERVAL = 5

ACCOUNT_SIZE = 100000
RISK = 0.02

SL = 0.002   # %0.2  (daha hızlı exit)
TP = 0.004   # %0.4
MAX_DURATION = 60  # saniye (hızlı time exit)

positions = {}
cooldown = {}
last_bar_time = {}
total_pnl = 0

# ================= TELEGRAM =================
def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=3
        )
    except:
        pass

# ================= DATA =================
def get_data(sym):
    try:
        df = yf.download(sym, period="1d", interval="1m", progress=False)
        if df is None or df.empty or len(df) < 30:
            return None

        df = df.copy().dropna()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return df

    except:
        return None

# ================= SIGNAL =================
def signal(df):
    try:
        last = df.iloc[-1]

        c = float(last["Close"])
        h = float(last["High"])
        l = float(last["Low"])
        t = last.name  # bar time

        rng = (h - l) + 1e-9
        buy = (c - l) / rng
        sell = (h - c) / rng

        if buy > 0.3:
            return "LONG", c, t
        if sell > 0.3:
            return "SHORT", c, t

    except:
        return None

    return None

# ================= MAIN =================
print("🚀 FAST PRO SYSTEM STARTED")
send("🚀 FAST PRO SYSTEM STARTED")

next_run = datetime.now()

while True:
    now = datetime.now()

    if now < next_run:
        continue

    next_run = now + timedelta(seconds=INTERVAL)

    print("⏱", now.strftime("%H:%M:%S"))

    for sym in SYMBOLS:

        df = get_data(sym)
        if df is None:
            continue

        s = signal(df)
        if s is None:
            continue

        side, price, bar_time = s

        # ================= EXIT =================
        if sym in positions:
            pos = positions[sym]

            entry = pos["entry"]
            size = pos["size"]
            entry_time = pos["time"]

            pnl = (price - entry) * size if pos["side"] == "LONG" else (entry - price) * size

            change = (price - entry) / entry if pos["side"] == "LONG" else (entry - price) / entry

            if change <= -SL:
                reason = "SL"
            elif change >= TP:
                reason = "TP"
            elif (now - entry_time).seconds > MAX_DURATION:
                reason = "TIME"
            else:
                continue

            print(f"❌ EXIT {sym} {reason} PnL:{pnl:.2f}")
            send(f"❌ EXIT {sym} {reason}\nPnL:{pnl:.2f}")

            total_pnl += pnl
            del positions[sym]
            cooldown[sym] = now
            continue

        # ================= COOLDOWN =================
        if sym in cooldown:
            if (now - cooldown[sym]).seconds < 30:
                continue

        # ================= SAME BAR FILTER =================
        if sym in last_bar_time:
            if last_bar_time[sym] == bar_time:
                continue

        # ================= ENTRY =================
        if len(positions) >= 3:
            continue

        size = round((ACCOUNT_SIZE * RISK) / price, 2)
        if size <= 0:
            continue

        positions[sym] = {
            "side": side,
            "entry": price,
            "size": size,
            "time": now
        }

        last_bar_time[sym] = bar_time

        msg = f"{side} {sym}\nPrice:{price:.2f}\nSize:{size}\nTotalPnL:{total_pnl:.2f}"
        print("🚀", msg)
        send(msg)