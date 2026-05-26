import yfinance as yf
import time

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

SCAN_INTERVAL = 5

SHORT_MA = 5
LONG_MA = 15

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

    # ENTRY
    if price > ma_short > ma_long and volume_up:
        return "BUY", price

    # EXIT
    if price < ma_short:
        return "SELL", price

    return "HOLD", price

print("🚀 SMART TRADE ENGINE STARTED")

while True:
    for s in SYMBOLS:
        df = get_data(s)

        if df is None or len(df) < LONG_MA:
            continue

        signal, price = get_signal(df)

        if s not in positions:
            if signal == "BUY":
                positions[s] = price
                print(f"🟢 BUY {s} | {price:.2f}")

        else:
            entry_price = positions[s]

            if signal == "SELL":
                pnl = price - entry_price
                print(f"🔴 SELL {s} | {price:.2f} | PnL:{pnl:.2f}")
                del positions[s]
            else:
                pnl = price - entry_price
                print(f"🟡 HOLD {s} | {price:.2f} | PnL:{pnl:.2f}")

    time.sleep(SCAN_INTERVAL)