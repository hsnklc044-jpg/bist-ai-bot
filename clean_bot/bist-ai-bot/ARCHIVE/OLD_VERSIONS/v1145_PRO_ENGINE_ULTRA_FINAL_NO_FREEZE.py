import yfinance as yf
import time
from datetime import datetime

SYMBOLS = ["TUPRS.IS", "EREGL.IS", "SISE.IS"]

SCAN_INTERVAL = 5
SHORT_MA = 5
LONG_MA = 20
TRAIL_PCT = 0.01

FREEZE_TOLERANCE = 3   # kaç bar aynı kalırsa freeze
MAX_FREEZE_WARN = 10   # log azaltma

positions = {}
last_bar_time = {}
freeze_counter = {}
freeze_warn_count = {}

# ================= DATA =================
def get_data(symbol, interval="1m"):
    df = yf.download(symbol, period="1d", interval=interval, progress=False)
    if df is None or df.empty:
        return None
    return df

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
        freeze_warn_count[symbol] = 0
        return False

    if current_bar == last_bar_time[symbol]:
        freeze_counter[symbol] += 1
    else:
        freeze_counter[symbol] = 0
        freeze_warn_count[symbol] = 0
        last_bar_time[symbol] = current_bar

    return freeze_counter[symbol] >= FREEZE_TOLERANCE

# ================= ENGINE =================
print("🚀 PRO ENGINE ULTRA FINAL NO FREEZE STARTED")

while True:
    now = datetime.now()

    for s in SYMBOLS:
        try:
            df = get_data(s, "1m")
            if df is None:
                continue

            # ===== FREEZE DETECT =====
            if is_frozen(s, df):

                freeze_warn_count[s] += 1

                # log spam azalt
                if freeze_warn_count[s] % MAX_FREEZE_WARN == 1:
                    print(f"❄️ FREEZE {s} → switching timeframe")

                # fallback → 5m data
                df = get_data(s, "5m")
                if df is None:
                    continue

            signal, price, ma_short = get_signal(df)
            if price is None:
                continue

            # ===== ENTRY =====
            if s not in positions and signal == "LONG":
                positions[s] = {
                    "entry": price,
                    "peak": price
                }
                print(f"🚀 ENTRY {s} | {price:.2f}")

            # ===== POSITION =====
            if s in positions:
                pos = positions[s]

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
                if price < ma_short:
                    pnl = price - pos["entry"]
                    print(f"⚠️ EXIT {s} | MA | PnL:{pnl:.2f}")
                    del positions[s]
                    continue

                pnl = price - pos["entry"]
                print(f"📊 {s} | {price:.2f} | PnL:{pnl:.2f}")

        except Exception as e:
            print(f"❌ ERROR {s}: {e}")

    time.sleep(SCAN_INTERVAL)