import time
import yfinance as yf
import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]
SCAN_INTERVAL = 5

positions = {}

TEST_MODE = True  # False yaparsan gerçek seans filtresi çalışır


# --- MARKET CHECK ---
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


# --- SIGNAL ---
def get_signal(df):
    close = df["Close"]
    volume = df["Volume"]

    if len(close) < 20:
        return "HOLD", 0.0

    price = close.iloc[-1].item()

    ma_short = close.rolling(5).mean().iloc[-1].item()
    ma_long = close.rolling(15).mean().iloc[-1].item()

    # MOMENTUM (YUMUŞAK)
    last3 = close.iloc[-3:].values
    momentum = (last3[2] > last3[1]) or (last3[1] > last3[0])

    # VOLUME
    vol_now = volume.iloc[-1].item()
    vol_avg = volume.rolling(10).mean().iloc[-1].item()
    volume_spike = vol_now > vol_avg * 1.2

    trend = price > ma_short

    if trend and momentum and volume_spike:
        return "BUY", price

    return "HOLD", price


# --- EXIT (TIME BASED) ---
def check_exit(symbol, price):
    entry_data = positions[symbol]

    entry_price = entry_data["price"]
    entry_time = entry_data["time"]

    pnl = price - entry_price

    # TRAILING STOP (%1)
    if price < entry_price * 0.99:
        return True, "TRAIL"

    # ⏱️ NO MOVE → 60 sn sonra kontrol
    if time.time() - entry_time > 60:
        if abs(price - entry_price) < entry_price * 0.002:
            return True, "NO MOVE"

    return False, None


print("🚀 PRO SMART TRADE TIME EXIT STARTED")

while True:

    if not is_market_open():
        print(f"⏸️ MARKET CLOSED | {datetime.datetime.now().strftime('%H:%M:%S')}")
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