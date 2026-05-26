import yfinance as yf
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

SCAN_INTERVAL = 5
SHORT_MA = 5
LONG_MA = 20
TRAIL_PCT = 0.01

EXIT_BUFFER = 0.002
MIN_HOLD = 15

FREEZE_TOLERANCE = 3
MAX_RETRY = 3
COOLDOWN = 60  # veri yoksa 60 sn bekle

positions = {}
last_bar_time = {}
freeze_counter = {}
fail_counter = {}
cooldown_map = {}

# ================= DATA =================
def get_data(symbol, interval="1m"):
    try:
        df = yf.download(symbol, period="1d", interval=interval, progress=False)
        if df is None or df.empty:
            return None
        return df
    except:
        return None

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
    current_bar = df.index[-1]

    if symbol not in last_bar_time:
        last_bar_time[symbol] = current_bar
        freeze_counter[symbol] = 0
        return False

    if current_bar == last_bar_time[symbol]:
        freeze_counter[symbol] += 1
    else:
        freeze_counter[symbol] = 0
        last_bar_time[symbol] = current_bar

    return freeze_counter[symbol] >= FREEZE_TOLERANCE

# ================= ENGINE =================
print("🚀 PRO ENGINE SMART RESILIENT STARTED")

while True:
    now = time.time()

    for s in SYMBOLS:
        try:
            # ===== COOLDOWN =====
            if s in cooldown_map and now < cooldown_map[s]:
                continue

            df = get_data(s, "1m")

            # ===== DATA FAIL =====
            if df is None:
                fail_counter[s] = fail_counter.get(s, 0) + 1
                print(f"⚠️ DATA FAIL {s} ({fail_counter[s]})")

                if fail_counter[s] >= MAX_RETRY:
                    print(f"⛔ COOLDOWN {s} 60s")
                    cooldown_map[s] = now + COOLDOWN
                    fail_counter[s] = 0
                continue

            # reset fail
            fail_counter[s] = 0

            # ===== FREEZE =====
            if is_frozen(s, df):
                print(f"❄️ FREEZE {s} → SKIP")
                continue

            signal, price, ma_short = get_signal(df)
            if price is None:
                continue

            # ===== ENTRY =====
            if s not in positions and signal == "LONG":
                positions[s] = {
                    "entry": price,
                    "peak": price,
                    "time": now
                }
                print(f"🚀 ENTRY {s} | {price:.2f}")

            # ===== POSITION =====
            if s in positions:
                pos = positions[s]

                if now - pos["time"] < MIN_HOLD:
                    print(f"⏳ HOLD {s}")
                    continue

                if price > pos["peak"]:
                    pos["peak"] = price

                trail = pos["peak"] * (1 - TRAIL_PCT)

                # TRAIL EXIT
                if price < trail:
                    pnl = price - pos["entry"]
                    print(f"🔻 EXIT {s} | TRAIL | PnL:{pnl:.2f}")
                    del positions[s]
                    continue

                # MA EXIT
                if price < ma_short * (1 - EXIT_BUFFER):
                    pnl = price - pos["entry"]
                    print(f"⚠️ EXIT {s} | MA | PnL:{pnl:.2f}")
                    del positions[s]
                    continue

                pnl = price - pos["entry"]
                print(f"📊 {s} | {price:.2f} | PnL:{pnl:.2f}")

        except Exception as e:
            print(f"❌ ERROR {s}: {e}")

    time.sleep(SCAN_INTERVAL)