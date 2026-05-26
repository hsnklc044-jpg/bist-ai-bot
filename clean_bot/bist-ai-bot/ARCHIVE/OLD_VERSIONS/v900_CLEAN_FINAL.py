import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta

TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

SYMBOLS = ["TUPRS.IS","EREGL.IS","SISE.IS"]

INTERVAL = 5  # saniye

ACCOUNT_SIZE = 100000
RISK = 0.02

positions = {}
total_pnl = 0

# ===== TELEGRAM =====
def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=3
        )
    except:
        pass

# ===== SAFE DATA =====
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

# ===== SIGNAL =====
def signal(df):
    try:
        last = df.iloc[-1]

        close = float(last["Close"])
        high = float(last["High"])
        low = float(last["Low"])

        rng = (high - low) + 1e-9

        buy = (close - low) / rng
        sell = (high - close) / rng

        if buy > 0.3:
            return "LONG", close

        if sell > 0.3:
            return "SHORT", close

    except:
        return None

    return None

# ===== MAIN =====
print("🚀 CLEAN FINAL STARTED")
send("🚀 CLEAN FINAL STARTED")

next_run = datetime.now()

while True:
    try:
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

            side, price = s

            # EXIT
            if sym in positions:
                entry = positions[sym]["entry"]
                size = positions[sym]["size"]

                pnl = (price - entry) * size if positions[sym]["side"]=="LONG" else (entry - price) * size

                # basit exit (profit veya zarar)
                if abs(pnl) > 50:
                    print(f"❌ EXIT {sym} PnL:{pnl:.2f}")
                    total_pnl += pnl
                    del positions[sym]
                    continue

                continue

            # ENTRY
            if len(positions) >= 3:
                continue

            size = round((ACCOUNT_SIZE * RISK) / price, 2)

            positions[sym] = {
                "side": side,
                "entry": price,
                "size": size
            }

            msg = f"{side} {sym}\nPrice:{price:.2f}\nSize:{size}\nPnL:{total_pnl:.2f}"

            print("🚀", msg)
            send(msg)

    except Exception as e:
        print("❌ ERROR:", e)