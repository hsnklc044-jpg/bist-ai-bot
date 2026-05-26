import requests
import time
import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import json
import os

warnings.filterwarnings("ignore")

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"
url = "https://api.telegram.org/bot" + TOKEN

symbols = ["THYAO","AKBNK","BIMAS","EREGL"]

capital = 100000
active_trades = []
locked_symbols = set()

MEMORY_FILE = "memory.json"
LOG_FILE = "trades_log.csv"

MAX_TRADES = 3
DRY_RUN = True

weights = {"trend":1.0,"scalp":1.0}

# ================= MEMORY =================
def save_memory():
    data = {
        "active_trades": active_trades,
        "locked_symbols": list(locked_symbols),
        "symbols": symbols,
        "weights": weights
    }
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

def load_memory():
    global active_trades, locked_symbols, symbols, weights

    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)

            raw = data.get("active_trades", [])
            cleaned = []

            for t in raw:
                if "symbol" not in t or "entry" not in t:
                    continue

                t.setdefault("tp", t["entry"] * 1.02)
                t.setdefault("sl", t["entry"] * 0.98)
                t.setdefault("lot", 1)
                t.setdefault("strategy", "trend")

                cleaned.append(t)

            active_trades = cleaned
            locked_symbols = set(data.get("locked_symbols", []))
            symbols = data.get("symbols", symbols)
            weights = data.get("weights", weights)

# ================= LOG FIX =================
def sanitize_log():
    if not os.path.exists(LOG_FILE):
        return

    df = pd.read_csv(LOG_FILE)

    if "strategy" not in df.columns:
        df["strategy"] = "trend"
        df.to_csv(LOG_FILE, index=False)

# ================= LOG =================
def log_trade(symbol, profit, strategy):
    exists = os.path.exists(LOG_FILE)

    with open(LOG_FILE, "a") as f:
        if not exists:
            f.write("symbol,profit,strategy\n")
        f.write(f"{symbol},{profit},{strategy}\n")

# ================= AI =================
def optimize_strategy():
    global weights

    if not os.path.exists(LOG_FILE):
        return

    df = pd.read_csv(LOG_FILE)

    if "strategy" not in df.columns:
        return

    if len(df) < 5:
        return

    perf = df.groupby("strategy")["profit"].sum()

    best = perf.idxmax()
    worst = perf.idxmin()

    weights[best] += 0.2
    weights[worst] -= 0.2

    weights[best] = min(weights[best], 2)
    weights[worst] = max(weights[worst], 0.5)

    send(f"⚖️ STRATEGY UPDATE\nBest: {best}\nWorst: {worst}")
    save_memory()

# ================= UTILS =================
def send(msg):
    try:
        requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def get_data(s):
    try:
        df = yf.download(s + ".IS", period="5d", interval="5m", progress=False)
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

def place_order(symbol, lot, strategy):
    if DRY_RUN:
        send(f"🧪 {strategy.upper()} {symbol} Lot:{lot}")
        return True
    else:
        send(f"✅ {strategy.upper()} REAL {symbol} Lot:{lot}")
        return True

# ================= START =================
load_memory()
sanitize_log()

print("AI TRADER V32.2 FIX CALISIYOR...")
send("🧠 V32.2 LOG FIX AKTİF")

while True:
    try:

        optimize_strategy()

        for s in symbols:

            if len(active_trades) >= MAX_TRADES:
                break

            if s in locked_symbols:
                continue

            df = get_data(s)
            if df is None:
                continue

            df["ATR"] = atr(df)
            price = float(df["Close"].iloc[-1])
            atr_v = float(df["ATR"].iloc[-1])

            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()

            ma20 = float(df["MA20"].iloc[-1])
            ma50 = float(df["MA50"].iloc[-1])
            momentum = float(df["Close"].iloc[-1] - df["Close"].iloc[-3])

            trend_score = 0
            if price > ma20: trend_score += 2
            if price > ma50: trend_score += 2
            if momentum > 0: trend_score += 2

            move = float(df["Close"].iloc[-1] - df["Close"].iloc[-2])

            scalp_score = 0
            if move > 0: scalp_score += 3
            if abs(move) > atr_v * 0.2: scalp_score += 3

            trend_score *= weights["trend"]
            scalp_score *= weights["scalp"]

            strategy = None

            if trend_score > scalp_score and trend_score >= 5:
                strategy = "trend"
                sl = price - atr_v * 1.5
                tp = price + atr_v * 3

            elif scalp_score >= 4:
                strategy = "scalp"
                sl = price - atr_v * 0.8
                tp = price + atr_v * 1.5

            if strategy is None:
                continue

            risk_pct = 0.005
            risk_amount = capital * risk_pct
            risk_per_share = price - sl

            if risk_per_share <= 0:
                continue

            lot = round(risk_amount / risk_per_share, 2)

            ok = place_order(s, lot, strategy)

            if ok:
                trade = {
                    "symbol": s,
                    "entry": price,
                    "tp": tp,
                    "sl": sl,
                    "lot": lot,
                    "strategy": strategy
                }

                active_trades.append(trade)
                locked_symbols.add(s)
                save_memory()

                send(f"🚀 {strategy.upper()} TRADE {s}")

        for t in active_trades[:]:

            df = get_data(t["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price >= t["tp"]:
                profit = (t["tp"] - t["entry"]) * t["lot"]
                capital += profit

                log_trade(t["symbol"], profit, t["strategy"])

                send(f"🟢 {t['strategy']} TP {t['symbol']} +{round(profit,2)}")

                active_trades.remove(t)
                locked_symbols.discard(t["symbol"])
                save_memory()

            elif price <= t["sl"]:
                loss = (t["entry"] - t["sl"]) * t["lot"]
                capital -= loss

                log_trade(t["symbol"], -loss, t["strategy"])

                send(f"🔴 {t['strategy']} SL {t['symbol']} -{round(loss,2)}")

                active_trades.remove(t)
                locked_symbols.discard(t["symbol"])
                save_memory()

    except Exception as e:
        print("HATA:", e)

    time.sleep(10)
