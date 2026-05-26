import yfinance as yf
import time

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

SCAN_INTERVAL = 5

SHORT_MA = 5
LONG_MA = 15

MAX_HOLD_TIME = 60      # saniye
MIN_MOVE = 0.001        # %0.1
TRAILING_STOP = 0.002   # %0.2

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

    price = close.iloc[-1].item()
    ma_short = close.rolling(SHORT_MA).mean().iloc[-1].item()
    ma_long = close.rolling(LONG_MA).mean().iloc[-1].item()

    volume = df["Volume"].iloc[-1].item()
    prev_volume = df["Volume"].iloc[-2].item()

    volume_up = volume > prev_volume

    if price > ma_short > ma_long and volume_up:
        return "BUY", price

    return "HOLD", price

print("🚀 SMART TRADE PRO STARTED")

while True:
    now = time.time()

    for s in SYMBOLS:
        df = get_data(s)

        if df is None or len(df) < LONG_MA:
            continue

        signal, price = get_signal(df)

        # --- ENTRY ---
        if s not in positions:
            if signal == "BUY":
                positions[s] = {
                    "entry": price,
                    "time": now,
                    "max_price": price
                }
                print(f"🟢 BUY {s} | {price:.2f}")

        # --- POSITION MANAGEMENT ---
        else:
            pos = positions[s]
            entry = pos["entry"]

            pnl = (price - entry) / entry

            # max price güncelle
            if price > pos["max_price"]:
                pos["max_price"] = price

            # trailing hesapla
            drop_from_peak = (pos["max_price"] - price) / pos["max_price"]

            hold_time = now - pos["time"]

            # 🔴 EXIT CONDITIONS
            if hold_time > MAX_HOLD_TIME:
                print(f"⏰ TIME EXIT {s} | {price:.2f} | PnL:{pnl:.3f}")
                del positions[s]

            elif abs(pnl) < MIN_MOVE and hold_time > 20:
                print(f"⚠️ NO MOVE EXIT {s} | {price:.2f}")
                del positions[s]

            elif drop_from_peak > TRAILING_STOP:
                print(f"📉 TRAIL EXIT {s} | {price:.2f} | PnL:{pnl:.3f}")
                del positions[s]

            else:
                print(f"🟡 HOLD {s} | {price:.2f} | PnL:{pnl:.3f}")

    time.sleep(SCAN_INTERVAL)