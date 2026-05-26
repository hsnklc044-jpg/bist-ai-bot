import yfinance as yf
import time

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

SCAN_INTERVAL = 5
FREEZE_LIMIT = 5

last_data = {}
freeze_counter = {}

def get_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False)
        if df is None or df.empty:
            return None
        return df
    except:
        return None

def is_frozen(symbol, df):
    last_row = df.iloc[-1]

    price = last_row["Close"]
    volume = last_row["Volume"]

    key = (price, volume)

    if symbol not in last_data:
        last_data[symbol] = key
        freeze_counter[symbol] = 0
        return False

    if key == last_data[symbol]:
        freeze_counter[symbol] += 1
    else:
        freeze_counter[symbol] = 0
        last_data[symbol] = key

    return freeze_counter[symbol] >= FREEZE_LIMIT

print("🚀 TRUE FREEZE FIX ENGINE STARTED")

while True:
    for s in SYMBOLS:
        df = get_data(s)

        if df is None:
            print(f"❌ DATA YOK {s}")
            continue

        if is_frozen(s, df):
            print(f"❄️ GERÇEK FREEZE {s}")
        else:
            price = df["Close"].iloc[-1]
            print(f"✅ AKTİF {s} | {price:.2f}")

    time.sleep(SCAN_INTERVAL)