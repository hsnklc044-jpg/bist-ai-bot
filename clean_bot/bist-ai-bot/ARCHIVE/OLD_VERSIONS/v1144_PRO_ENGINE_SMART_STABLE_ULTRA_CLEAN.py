import yfinance as yf
import pandas as pd
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

SCAN_INTERVAL = 5
SHORT_MA = 5
LONG_MA = 20
TRAIL_PCT = 0.01
MAX_FREEZE = 30

positions = {}
last_bar_time = {}

# ================= DATA =================
def get_data(symbol):
    df = yf.download(symbol, period="1d", interval="1m", progress=False)
    if df is None or df.empty:
        return None
    return df

# ================= SIGNAL =================
def get_signal(df):
    if len(df) < LONG_MA:
        return None, None, None

    close = df["Close"]

    price = close.iloc[-1].item()
    ma_short = close.rolling(SHORT_MA).mean().iloc[-1].item()
    ma_long = close.rolling(LONG_MA).mean().iloc[-1].item()

    if ma_short > ma_long:
        return "LONG", price, ma_short
    return None, price, ma_short

# ================= FREEZE =================
def is_frozen(symbol, df):
    global last_bar_time

    current_bar = df.index[-1]

    if symbol not in last_bar_time:
        last_bar_time[symbol] = current_bar
        return False

    if current_bar == last_bar_time[symbol]:
        return True

    last_bar_time[symbol] = current_bar
    return False

print("🚀 PRO ENGINE SMART STABLE ULTRA CLEAN STARTED")

# ================= LOOP =================
while True:
    now = datetime.now()

    for s in SYMBOLS:
        try:
            df = get_data(s)
            if df is None:
                continue

            # 🔥 FREEZE CONTROL
            if is_frozen(s, df):
                print(f"❄️ FREEZE {s} → SKIP")
                continue

            signal, price, ma_short = get_signal(df)
            if price is None:
                continue

            # ================= ENTRY =================
            if s not in positions and signal == "LONG":
                positions[s] = {
                    "entry": price,
                    "peak": price
                }
                print(f"🚀 ENTRY {s} | {price:.2f}")

            # ================= POSITION =================
            if s in positions:
                pos = positions[s]

                # peak update
                if price > pos["peak"]:
                    pos["peak"] = price

                trail_stop = pos["peak"] * (1 - TRAIL_PCT)

                # TRAIL EXIT
                if price < trail_stop:
                    pnl = price - pos["entry"]
                    print(f"🔻 EXIT {s} | TRAIL | PnL:{pnl:.2f}")
                    del positions[s]
                    continue

                # MA EXIT
                if price < ma_short:
                    pnl = price - pos["entry"]
                    print(f"⚠️ EXIT {s} | MA | PnL:{pnl:.2f}")
                    del positions[s]
                    continue

                pnl = price - pos["entry"]
                print(f"📊 {s} | {price:.2f} | PnL:{pnl:.2f}")

        except Exception as e:
            print(f"❌ ERROR {s}: {e}")

    time.sleep(SCAN_INTERVAL)