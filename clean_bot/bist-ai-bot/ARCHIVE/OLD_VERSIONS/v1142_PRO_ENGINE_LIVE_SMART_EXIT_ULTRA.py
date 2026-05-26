import yfinance as yf
import pandas as pd
import time

# ================= CONFIG =================
SYMBOLS = ["EREGL.IS", "TUPRS.IS", "SISE.IS"]
SCAN_INTERVAL = 5

MA_PERIOD = 20
TRAIL_PCT = 0.5 / 100
MAX_IDLE = 120
MAX_FREEZE = 20

positions = {}
last_prices = {}
last_update_time = {}

# ================= DATA =================
def get_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False)
        if df.empty:
            return None
        return df
    except:
        return None

# ================= SIGNAL =================
def get_signal(df):
    close = df["Close"]
    ma = close.rolling(MA_PERIOD).mean()

    if len(close) < MA_PERIOD:
        return None, None

    # SAFE FLOAT
    c1 = float(close.iloc[-1].item())
    c2 = float(close.iloc[-2].item())
    c3 = float(close.iloc[-3].item())
    ma_val = float(ma.iloc[-1].item())

    # NO MOVE FILTER
    if c1 == c2 and c2 == c3:
        return "NO_MOVE", c1

    if c1 > ma_val:
        return "LONG", c1

    return None, c1

# ================= ENGINE =================
print("🚀 PRO ENGINE LIVE SMART EXIT ULTRA STARTED")

while True:
    print(f"\n⏰ {pd.Timestamp.now()}")

    for s in SYMBOLS:
        df = get_data(s)

        if df is None:
            print(f"⚠️ DATA ERROR {s}")
            continue

        signal, price = get_signal(df)

        if price is None:
            continue

        now = time.time()

        # ================= DATA FREEZE FILTER =================
        if s in last_prices:
            if price == last_prices[s]:
                freeze_time = now - last_update_time[s]

                if freeze_time > MAX_FREEZE:
                    print(f"❄️ DATA FREEZE {s} ({int(freeze_time)}s)")

                    # 🔥 FREEZE EXIT
                    if s in positions:
                        pos = positions[s]
                        pnl = price - pos["entry"]
                        print(f"🚨 EXIT {s} | DATA FREEZE | PnL:{pnl:.2f}")
                        del positions[s]

                    continue
            else:
                last_update_time[s] = now
        else:
            last_update_time[s] = now

        last_prices[s] = price

        # ================= ENTRY =================
        if s not in positions:
            if signal == "LONG":
                positions[s] = {
                    "entry": price,
                    "peak": price,
                    "entry_time": now
                }
                print(f"🚀 ENTRY {s} | price:{price:.2f}")

            elif signal == "NO_MOVE":
                print(f"⏸ SKIP {s} | no real move")

        # ================= POSITION =================
        else:
            pos = positions[s]
            entry = pos["entry"]
            peak = pos["peak"]

            pnl = price - entry

            # update peak
            if price > peak:
                pos["peak"] = price

            trail_price = pos["peak"] * (1 - TRAIL_PCT)

            print(f"📊 {s} | price:{price:.2f} | pnl:{pnl:.2f}")

            # ================= TRAIL EXIT =================
            if price < trail_price:
                print(f"❌ EXIT {s} | TRAIL | PnL:{pnl:.2f}")
                del positions[s]
                continue

            # ================= TIME EXIT =================
            idle_time = now - pos["entry_time"]

            if idle_time > MAX_IDLE:
                print(f"⏰ EXIT {s} | TIMEOUT | PnL:{pnl:.2f}")
                del positions[s]
                continue

    time.sleep(SCAN_INTERVAL)