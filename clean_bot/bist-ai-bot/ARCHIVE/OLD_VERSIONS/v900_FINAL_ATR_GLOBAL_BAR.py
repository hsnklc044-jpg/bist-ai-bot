import yfinance as yf
import requests
import pandas as pd
from datetime import datetime
import time

# ================= CONFIG =================
TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

SYMBOLS = ["TUPRS.IS","EREGL.IS","SISE.IS"]

ACCOUNT_SIZE = 100000
RISK = 0.02

ATR_MULT_SL = 1.2
ATR_MULT_TP = 2.0

MAX_DURATION = 180  # saniye

positions = {}
cooldown = {}
total_pnl = 0

# 🔥 GLOBAL BAR
last_global_bar = None

# ================= TELEGRAM =================
def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=3
        )
    except:
        pass

# ================= ATR =================
def calculate_atr(df, period=14):
    high = df['High']
    low = df['Low']
    close = df['Close']

    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)

    return tr.rolling(period).mean()

# ================= DATA =================
def get_data(sym):
    try:
        df = yf.download(sym, period="1d", interval="1m", progress=False)

        if df is None or df.empty or len(df) < 30:
            return None

        df = df.copy().dropna()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df["ATR"] = calculate_atr(df)

        return df

    except:
        return None

# ================= SIGNAL =================
def signal(df):
    last = df.iloc[-1]

    c = float(last["Close"])
    h = float(last["High"])
    l = float(last["Low"])
    atr = float(last["ATR"])

    rng = (h - l) + 1e-9

    buy = (c - l) / rng
    sell = (h - c) / rng

    if buy > 0.3:
        return "LONG", c, atr

    if sell > 0.3:
        return "SHORT", c, atr

    return None

# ================= MAIN =================
print("🚀 FINAL GLOBAL ATR ENGINE STARTED")
send("🚀 FINAL GLOBAL ATR ENGINE STARTED")

while True:
    try:
        # 🔥 REFERANS SEMBOL (GLOBAL BAR)
        df_ref = get_data(SYMBOLS[0])
        if df_ref is None:
            time.sleep(5)
            continue

        current_bar = df_ref.index[-1].to_pydatetime()

        # 🔥 GLOBAL BAR KONTROLÜ
        if last_global_bar == current_bar:
            time.sleep(5)
            continue

        last_global_bar = current_bar
        now = datetime.now()

        print("\n⏱ NEW BAR:", now.strftime("%H:%M:%S"))

        # ================= TÜM HİSSELER =================
        for sym in SYMBOLS:

            df = get_data(sym)
            if df is None:
                continue

            s = signal(df)
            if s is None:
                continue

            side, price, atr = s

            # ================= EXIT =================
            if sym in positions:
                pos = positions[sym]

                entry = pos["entry"]
                size = pos["size"]
                entry_time = pos["time"]
                atr_entry = pos["atr"]

                pnl = (price - entry) * size if pos["side"] == "LONG" else (entry - price) * size

                sl = atr_entry * ATR_MULT_SL
                tp = atr_entry * ATR_MULT_TP

                if pos["side"] == "LONG":
                    if price <= entry - sl:
                        reason = "SL"
                    elif price >= entry + tp:
                        reason = "TP"
                    elif (now - entry_time).seconds > MAX_DURATION:
                        reason = "TIME"
                    else:
                        continue
                else:
                    if price >= entry + sl:
                        reason = "SL"
                    elif price <= entry - tp:
                        reason = "TP"
                    elif (now - entry_time).seconds > MAX_DURATION:
                        reason = "TIME"
                    else:
                        continue

                print(f"❌ EXIT {sym} {reason} PnL:{pnl:.2f}")
                send(f"❌ EXIT {sym} {reason}\nPnL:{pnl:.2f}")

                total_pnl += pnl
                del positions[sym]
                cooldown[sym] = now
                continue

            # ================= COOLDOWN =================
            if sym in cooldown:
                if (now - cooldown[sym]).seconds < 60:
                    continue

            # ================= ENTRY =================
            if len(positions) >= 3:
                continue

            size = round((ACCOUNT_SIZE * RISK) / price, 2)

            positions[sym] = {
                "side": side,
                "entry": price,
                "size": size,
                "time": now,
                "atr": atr
            }

            msg = f"{side} {sym}\nPrice:{price:.2f}\nATR:{atr:.2f}\nTotalPnL:{total_pnl:.2f}"

            print("🚀", msg)
            send(msg)

        time.sleep(2)

    except Exception as e:
        print("❌ ERROR:", e)
        time.sleep(5)