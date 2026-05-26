import requests
import time
import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import json
import os

warnings.filterwarnings("ignore")

# ================= CONFIG =================
TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"
url = "https://api.telegram.org/bot" + TOKEN

symbols = ["THYAO","AKBNK","BIMAS","EREGL"]

capital = 100000
active_trades = []
locked_symbols = set()

MEMORY_FILE = "memory.json"
LOG_FILE = "trades_log.csv"

MAX_TRADES = 2
DRY_RUN = True

# ================= MEMORY =================
def save_memory():
    data = {
        "active_trades": active_trades,
        "locked_symbols": list(locked_symbols),
        "symbols": symbols
    }
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

def load_memory():
    global active_trades, locked_symbols, symbols

    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)

            raw_trades = data.get("active_trades", [])
            cleaned_trades = []

            for t in raw_trades:
                if "symbol" not in t or "entry" not in t:
                    continue
                t.setdefault("tp", t["entry"] * 1.02)
                t.setdefault("sl", t["entry"] * 0.98)
                t.setdefault("lot", 1)
                cleaned_trades.append(t)

            active_trades = cleaned_trades
            locked_symbols = set(data.get("locked_symbols", []))
            symbols = data.get("symbols", symbols)

# ================= LOG =================
def log_trade(symbol, profit):
    exists = os.path.exists(LOG_FILE)

    with open(LOG_FILE, "a") as f:
        if not exists:
            f.write("symbol,profit\n")
        f.write(f"{symbol},{profit}\n")

# ================= AI LEARNING =================
def optimize_symbols():
    global symbols

    if not os.path.exists(LOG_FILE):
        return

    df = pd.read_csv(LOG_FILE)

    if len(df) < 5:
        return

    grouped = df.groupby("symbol")["profit"].sum()

    best = grouped.idxmax()
    worst = grouped.idxmin()

    new_symbols = list(set(symbols))

    # kötü çıkar
    if grouped[worst] < 0 and worst in new_symbols:
        new_symbols.remove(worst)
        send(f"⛔ {worst} sistemden çıkarıldı")

    # iyi ekle
    if best not in new_symbols:
        new_symbols.append(best)
        send(f"🚀 {best} sisteme eklendi")

    symbols = new_symbols
    save_memory()

# ================= UTILS =================
def send(msg):
    try:
        requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def get_data(s):
    try:
        df = yf.download(s + ".IS", period="5d", interval="15m", progress=False)
        return df if df is not None and not df.empty else None
    except:
        return None

def atr(df):
    tr = pd.concat([
        df["High"] - df["Low"],
        abs(df["High"] - df["Close"].shift()),
        abs(df["Low"] - df["Close"].shift())
    ], axis=1)
    return tr.max(axis=1).rolling(14).mean()

def place_order(symbol, lot):
    if DRY_RUN:
        send(f"🧪 AUTO DRY RUN {symbol} Lot:{lot}")
        return True
    else:
        send(f"✅ REAL ORDER {symbol} Lot:{lot}")
        return True

# ================= START =================
load_memory()

print("AI TRADER V30 SELF LEARNING CALISIYOR...")
send("🧠 V30 SELF LEARNING AKTİF")

while True:
    try:

        # 💣 OPTIMIZATION
        optimize_symbols()

        # ================= OPEN =================
        for s in symbols:

            if len(active_trades) >= MAX_TRADES:
                break

            if s in locked_symbols:
                continue

            df = get_data(s)
            if df is None:
                continue

            df["ATR"] = atr(df)
            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()

            price = float(df["Close"].iloc[-1])
            atr_v = float(df["ATR"].iloc[-1])
            ma20 = float(df["MA20"].iloc[-1])
            ma50 = float(df["MA50"].iloc[-1])

            momentum = float(df["Close"].iloc[-1] - df["Close"].iloc[-3])

            score = 0
            if price > ma20: score += 2
            if price > ma50: score += 2
            if momentum > 0: score += 2

            if score < 5:
                continue

            sl = price - atr_v * 1.5
            tp = price + atr_v * 3

            risk_pct = 0.005
            risk_amount = capital * risk_pct
            risk_per_share = price - sl

            if risk_per_share <= 0:
                continue

            lot = round(risk_amount / risk_per_share, 2)

            ok = place_order(s, lot)

            if ok:
                trade = {
                    "symbol": s,
                    "entry": price,
                    "tp": tp,
                    "sl": sl,
                    "lot": lot
                }

                active_trades.append(trade)
                locked_symbols.add(s)
                save_memory()

                send(f"🚀 AUTO TRADE {s} Lot:{lot}")

        # ================= CLOSE =================
        for t in active_trades[:]:

            df = get_data(t["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price >= t["tp"]:
                profit = (t["tp"] - t["entry"]) * t["lot"]
                capital += profit

                log_trade(t["symbol"], profit)

                send(f"🟢 TP {t['symbol']} +{round(profit,2)}")

                active_trades.remove(t)
                locked_symbols.discard(t["symbol"])
                save_memory()

            elif price <= t["sl"]:
                loss = (t["entry"] - t["sl"]) * t["lot"]
                capital -= loss

                log_trade(t["symbol"], -loss)

                send(f"🔴 SL {t['symbol']} -{round(loss,2)}")

                active_trades.remove(t)
                locked_symbols.discard(t["symbol"])
                save_memory()

    except Exception as e:
        print("HATA:", e)

    time.sleep(10)
