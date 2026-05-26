import yfinance as yf
import pandas as pd
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

SCAN_INTERVAL = 5
SHORT_MA = 5
LONG_MA = 20
TRAIL_PCT = 0.01
MAX_FREEZE = 30  # saniye

positions = {}
last_update_time = {}

def get_data(symbol):
    df = yf.download(symbol, period="1d", interval="1m", progress=False)
    return df

def get_signal(df):
    if df is None or len(df) < LONG_MA:
        return None, None, None

    close = df["Close"]

    price = float(close.iloc[-1])
    ma_short = float(close.rolling(SHORT_MA).mean().iloc[-1])
    ma_long = float(close.rolling(LONG_MA).mean().iloc[-1])

    if ma_short > ma_long:
        return "LONG", price, ma_short
    else:
        return None, price, ma_short


def check_freeze(symbol, df):
    global last_update_time

    last_idx = df.index[-1]

    if symbol not in last_update_time:
        last_update_time[symbol] = last_idx
        return False

    if last_idx == last_update_time[symbol]:
        return True
    else:
        last_update_time[symbol] = last_idx
        return False


print("🚀 PRO ENGINE SMART STABLE ULTRA STARTED")

while True:
    now = datetime.now()

    for s in SYMBOLS:
        try:
            df = get_data(s)

            if df is None or df.empty:
                continue

            # 🔥 FREEZE CHECK (DOĞRU YÖNTEM)
            if check_freeze(s, df):
                print(f"❄️ DATA FREEZE {s}")
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
                print(f"🚀 ENTRY {s} | price:{price:.2f}")

            # ================= POSITION =================
            if s in positions:
                pos = positions[s]

                # peak update
                if price > pos["peak"]:
                    pos["peak"] = price

                trail_stop = pos["peak"] * (1 - TRAIL_PCT)

                # EXIT 1: TRAILING STOP
                if price < trail_stop:
                    pnl = price - pos["entry"]
                    print(f"🔻 EXIT {s} | TRAIL | PnL:{pnl:.2f}")
                    del positions[s]
                    continue

                # EXIT 2: MA BREAK
                if price < ma_short:
                    pnl = price - pos["entry"]
                    print(f"⚠️ EXIT {s} | MA BREAK | PnL:{pnl:.2f}")
                    del positions[s]
                    continue

                # HOLD
                pnl = price - pos["entry"]
                print(f"📊 {s} | price:{price:.2f} | pnl:{pnl:.2f}")

        except Exception as e:
            print(f"ERROR {s}: {e}")

    time.sleep(SCAN_INTERVAL)