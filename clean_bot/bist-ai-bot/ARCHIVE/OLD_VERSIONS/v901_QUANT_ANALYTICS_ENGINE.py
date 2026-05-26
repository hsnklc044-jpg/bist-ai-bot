import yfinance as yf
import requests
import pandas as pd
from datetime import datetime
import time, csv, os

# ================= CONFIG =================
TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

SYMBOLS = ["TUPRS.IS","EREGL.IS","SISE.IS"]

ACCOUNT_SIZE = 100000
RISK = 0.02

ATR_MULT_SL = 1.2
ATR_MULT_TP = 2.0
MAX_DURATION = 180

LOG_FILE = "trades_log.csv"

positions = {}
cooldown = {}
total_pnl = 0
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

# ================= LOG =================
def log_trade(row):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "time","symbol","side","entry","exit","pnl","reason"
            ])
        writer.writerow(row)

# ================= ATR =================
def atr(df, p=14):
    tr = pd.concat([
        df['High']-df['Low'],
        (df['High']-df['Close'].shift()).abs(),
        (df['Low']-df['Close'].shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(p).mean()

# ================= DATA =================
def get(sym):
    try:
        df = yf.download(sym, period="1d", interval="1m", progress=False)
        if df is None or df.empty or len(df)<30:
            return None
        df = df.copy().dropna()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df["ATR"] = atr(df)
        return df
    except:
        return None

# ================= SIGNAL =================
def signal(df):
    last = df.iloc[-1]
    c = float(last["Close"])
    h = float(last["High"])
    l = float(last["Low"])
    a = float(last["ATR"])

    rng = (h-l)+1e-9
    buy = (c-l)/rng
    sell = (h-c)/rng

    if buy>0.3:
        return "LONG", c, a
    if sell>0.3:
        return "SHORT", c, a
    return None

# ================= ANALYTICS =================
def report():
    try:
        df = pd.read_csv(LOG_FILE)
        if len(df)==0:
            return "No trades yet"

        total = df["pnl"].sum()
        wins = df[df["pnl"]>0]
        losses = df[df["pnl"]<=0]

        winrate = len(wins)/len(df)*100
        avg_win = wins["pnl"].mean() if len(wins)>0 else 0
        avg_loss = losses["pnl"].mean() if len(losses)>0 else 0

        return f"""
📊 PERFORMANCE

Trades: {len(df)}
Winrate: {winrate:.2f}%
Total PnL: {total:.2f}

Avg Win: {avg_win:.2f}
Avg Loss: {avg_loss:.2f}
"""
    except:
        return "Report error"

# ================= MAIN =================
print("🚀 QUANT ANALYTICS ENGINE STARTED")
send("🚀 QUANT ANALYTICS ENGINE STARTED")

last_report_time = datetime.now()

while True:
    try:
        df_ref = get(SYMBOLS[0])
        if df_ref is None:
            time.sleep(5)
            continue

        current_bar = df_ref.index[-1].to_pydatetime()

        if last_global_bar == current_bar:
            time.sleep(5)
            continue

        last_global_bar = current_bar
        now = datetime.now()

        print("\n⏱ NEW BAR:", now.strftime("%H:%M:%S"))

        for sym in SYMBOLS:

            df = get(sym)
            if df is None:
                continue

            s = signal(df)
            if s is None:
                continue

            side, price, atr_v = s

            # ===== EXIT =====
            if sym in positions:
                pos = positions[sym]
                entry = pos["entry"]
                size = pos["size"]
                entry_time = pos["time"]
                atr_entry = pos["atr"]

                pnl = (price-entry)*size if pos["side"]=="LONG" else (entry-price)*size

                sl = atr_entry*ATR_MULT_SL
                tp = atr_entry*ATR_MULT_TP

                if pos["side"]=="LONG":
                    if price <= entry-sl:
                        reason="SL"
                    elif price >= entry+tp:
                        reason="TP"
                    elif (now-entry_time).seconds>MAX_DURATION:
                        reason="TIME"
                    else:
                        continue
                else:
                    if price >= entry+sl:
                        reason="SL"
                    elif price <= entry-tp:
                        reason="TP"
                    elif (now-entry_time).seconds>MAX_DURATION:
                        reason="TIME"
                    else:
                        continue

                print(f"❌ EXIT {sym} {reason} {pnl:.2f}")
                send(f"❌ EXIT {sym} {reason}\nPnL:{pnl:.2f}")

                total_pnl += pnl

                log_trade([
                    now, sym, pos["side"],
                    entry, price, pnl, reason
                ])

                del positions[sym]
                cooldown[sym] = now
                continue

            # ===== COOLDOWN =====
            if sym in cooldown:
                if (now-cooldown[sym]).seconds<60:
                    continue

            # ===== ENTRY =====
            if len(positions)>=3:
                continue

            size = round((ACCOUNT_SIZE*RISK)/price,2)

            positions[sym] = {
                "side": side,
                "entry": price,
                "size": size,
                "time": now,
                "atr": atr_v
            }

            print(f"🚀 {side} {sym} {price}")

        # ===== AUTO REPORT =====
        if (now - last_report_time).seconds > 300:
            rep = report()
            print(rep)
            send(rep)
            last_report_time = now

    except Exception as e:
        print("ERROR:", e)

    time.sleep(5)