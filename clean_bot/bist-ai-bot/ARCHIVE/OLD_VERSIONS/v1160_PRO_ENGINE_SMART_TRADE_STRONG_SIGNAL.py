import time
import yfinance as yf
import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]
SCAN_INTERVAL = 5

positions = {}

TEST_MODE = True


# --- MARKET ---
def is_market_open():
    if TEST_MODE:
        return True

    now = datetime.datetime.now()
    start = now.replace(hour=9, minute=40, second=0)
    end = now.replace(hour=18, minute=10, second=0)

    return start <= now <= end


# --- DATA ---
def get_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False)

        if df is None or df.empty:
            df = yf.download(symbol, period="1d", interval="5m", progress=False)

        if df is None or df.empty:
            return None

        return df

    except:
        return None


# --- SIGNAL (STRONG) ---
def get_signal(df):
    close = df["Close"]
    volume = df["Volume"]

    if len(close) < 30:
        return "HOLD", 0.0

    price = close.iloc[-1].item()

    ma_short = close.rolling(5).mean().iloc[-1].item()
    ma_mid = close.rolling(10).mean().iloc[-1].item()
    ma_long = close.rolling(20).mean().iloc[-1].item()

    # 🔥 TREND GÜÇLÜ
    strong_trend = ma_short > ma_mid > ma_long

    # 🔥 MOMENTUM NET (3 mum üst üste yükseliş)
    last3 = close.iloc[-3:].values
    momentum = last3[2] > last3[1] > last3[0]

    # 🔥 HACİM PATLAMASI
    vol_now = volume.iloc[-1].item()
    vol_avg = volume.rolling(10).mean().iloc[-1].item()
    volume_spike = vol_now > vol_avg * 1.5

    if strong_trend and momentum and volume_spike:
        return "BUY", price

    return "HOLD", price


# --- EXIT ---
def check_exit(symbol, price):
    entry_data = positions[symbol]

    entry_price = entry_data["price"]
    entry_time = entry_data["time"]

    pnl = price - entry_price

    # 🔴 STOP
    if price < entry_price * 0.99:
        return True, "STOP"

    # 🟢 KAR AL
    if price > entry_price * 1.01:
        return True, "TAKE PROFIT"

    # ⏱️ NO MOVE
    if time.time() - entry_time > 90:
        if abs(price - entry_price) < entry_price * 0.003:
            return True, "NO MOVE"

    return False, None


print("🚀 PRO SMART TRADE STRONG SIGNAL STARTED")

while True:

    if not is_market_open():
        print(f"⏸️ MARKET CLOSED")
        time.sleep(60)
        continue

    for symbol in SYMBOLS:

        df = get_data(symbol)

        if df is None:
            print(f"❌ DATA YOK {symbol}")
            continue

        signal, price = get_signal(df)

        # ENTRY
        if symbol not in positions and signal == "BUY":
            positions[symbol] = {
                "price": price,
                "time": time.time()
            }
            print(f"🟢 BUY {symbol} | {price:.2f}")

        # POSITION
        elif symbol in positions:
            entry_price = positions[symbol]["price"]
            pnl = price - entry_price

            exit_flag, reason = check_exit(symbol, price)

            if exit_flag:
                print(f"🔴 EXIT {symbol} | {reason} | PnL:{pnl:.2f}")
                del positions[symbol]
            else:
                print(f"🟡 HOLD {symbol} | {price:.2f} | PnL:{pnl:.2f}")

        else:
            print(f"⏸️ SKIP {symbol}")

        time.sleep(1.5)

    print("-" * 40)
    time.sleep(SCAN_INTERVAL)