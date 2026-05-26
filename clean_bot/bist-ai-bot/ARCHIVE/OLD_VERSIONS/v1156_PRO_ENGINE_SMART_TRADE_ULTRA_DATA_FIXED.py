import time
import yfinance as yf
import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]
SCAN_INTERVAL = 5

positions = {}

# --- MARKET CHECK ---
def is_market_open():
    now = datetime.datetime.now()
    return 10 <= now.hour <= 18


# --- DATA (FALLBACK SYSTEM) ---
def get_data(symbol):
    try:
        # 1m dene
        df = yf.download(symbol, period="1d", interval="1m", progress=False)

        # fallback 5m
        if df is None or df.empty:
            df = yf.download(symbol, period="1d", interval="5m", progress=False)

        if df is None or df.empty:
            return None

        return df

    except:
        return None


# --- SIGNAL ---
def get_signal(df):
    close = df["Close"]
    volume = df["Volume"]

    if len(close) < 20:
        return "HOLD", 0.0

    price = close.iloc[-1].item()

    ma_short = close.rolling(5).mean().iloc[-1].item()
    ma_long = close.rolling(15).mean().iloc[-1].item()

    # momentum fix
    last3 = close.iloc[-3:].values
    momentum = (last3[2] > last3[1]) and (last3[1] > last3[0])

    # volume spike
    vol_now = volume.iloc[-1].item()
    vol_avg = volume.rolling(10).mean().iloc[-1].item()
    volume_spike = vol_now > vol_avg * 1.5

    if price > ma_short > ma_long and momentum and volume_spike:
        return "BUY", price

    return "HOLD", price


# --- EXIT ---
def check_exit(symbol, price):
    entry = positions[symbol]

    if price < entry * 0.99:
        return True, "TRAIL"

    if abs(price - entry) < entry * 0.001:
        return True, "NO MOVE"

    return False, None


print("🚀 PRO SMART TRADE ULTRA (DATA FIXED) STARTED")

while True:

    # --- MARKET CLOSED ---
    if not is_market_open():
        print("⏸️ MARKET CLOSED")
        time.sleep(60)
        continue

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

        else:
            print(f"⏸️ SKIP {symbol}")

        # 🔥 RATE LIMIT FIX
        time.sleep(1.5)

    print("-" * 40)
    time.sleep(SCAN_INTERVAL)