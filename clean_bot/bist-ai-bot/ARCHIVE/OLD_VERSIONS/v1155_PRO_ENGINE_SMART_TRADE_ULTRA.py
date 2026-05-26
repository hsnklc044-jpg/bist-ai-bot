import time
import yfinance as yf
import pandas as pd

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]
SCAN_INTERVAL = 5

positions = {}

def get_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False)
        if df is None or df.empty:
            return None
        return df
    except:
        return None

def get_signal(df):
    close = df["Close"]
    volume = df["Volume"]

    # --- SAFE SCALAR ---
    price = close.iloc[-1].item()

    ma_short = close.rolling(5).mean().iloc[-1].item()
    ma_long = close.rolling(15).mean().iloc[-1].item()

    # --- MOMENTUM (SON 3 BAR YUKARI) ---
    last3 = close.iloc[-3:]
    momentum = last3.iloc[-1] > last3.iloc[-2] > last3.iloc[-3]

    # --- VOLUME SPIKE ---
    vol_now = volume.iloc[-1].item()
    vol_avg = volume.rolling(10).mean().iloc[-1].item()
    volume_spike = vol_now > vol_avg * 1.5

    # --- SIGNAL ---
    if price > ma_short > ma_long and momentum and volume_spike:
        return "BUY", price

    return "HOLD", price

def check_exit(symbol, price):
    entry = positions[symbol]

    # --- TRAILING STOP (%1) ---
    if price < entry * 0.99:
        return True, "TRAIL"

    # --- NO MOVE EXIT ---
    if abs(price - entry) < entry * 0.001:
        return True, "NO MOVE"

    return False, None


print("🚀 PRO SMART TRADE ULTRA STARTED")

while True:
    for symbol in SYMBOLS:
        df = get_data(symbol)

        if df is None:
            print(f"❌ DATA YOK {symbol}")
            continue

        signal, price = get_signal(df)

        # --- ENTRY ---
        if symbol not in positions and signal == "BUY":
            positions[symbol] = price
            print(f"🟢 BUY {symbol} | {price:.2f}")

        # --- POSITION ---
        elif symbol in positions:
            entry_price = positions[symbol]
            pnl = price - entry_price

            exit_flag, reason = check_exit(symbol, price)

            if exit_flag:
                print(f"🔴 EXIT {symbol} | {reason} | PnL:{pnl:.2f}")
                del positions[symbol]
            else:
                print(f"🟡 HOLD {symbol} | {price:.2f} | PnL:{pnl:.2f}")

        # --- NO SIGNAL ---
        else:
            print(f"⏸️ SKIP {symbol}")

    print("-" * 40)
    time.sleep(SCAN_INTERVAL)