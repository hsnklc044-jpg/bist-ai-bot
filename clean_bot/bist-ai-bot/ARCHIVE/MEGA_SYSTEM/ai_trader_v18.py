import requests
import time
import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import json

warnings.filterwarnings("ignore")

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"
url = "https://api.telegram.org/bot" + TOKEN

symbols = ["THYAO","YKBNK","AKBNK","BIMAS","EREGL"]

SIM_MODE = True
active_trades = []
capital = 100000

perf_file = "strategy_perf.json"
alloc_file = "strategy_alloc.json"

default_perf = {
    "trend": {"win":0,"loss":0},
    "scalp": {"win":0,"loss":0},
    "reversal": {"win":0,"loss":0}
}

default_alloc = {
    "trend": 0.33,
    "scalp": 0.33,
    "reversal": 0.34
}

# yükle
try:
    with open(perf_file,"r") as f:
        perf = json.load(f)
except:
    perf = default_perf

try:
    with open(alloc_file,"r") as f:
        alloc = json.load(f)
except:
    alloc = default_alloc

def save_all():
    with open(perf_file,"w") as f:
        json.dump(perf,f)
    with open(alloc_file,"w") as f:
        json.dump(alloc,f)

def send(msg):
    try:
        requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def get_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="5d", interval="15m", progress=False)
        if df is None or df.empty:
            return None
        return df
    except:
        return None

def rsi(df):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    rs = gain.rolling(14).mean() / loss.rolling(14).mean()
    return 100 - (100 / (1 + rs))

def atr(df):
    tr = pd.concat([
        df["High"] - df["Low"],
        abs(df["High"] - df["Close"].shift()),
        abs(df["Low"] - df["Close"].shift())
    ], axis=1)
    return tr.max(axis=1).rolling(14).mean()

def detect_market(df):
    close = df["Close"]
    if len(close) < 20:
        return "neutral"
    change = float(close.iloc[-1]) - float(close.iloc[-10])
    if change > 2:
        return "trend"
    elif change < -2:
        return "down"
    else:
        return "sideways"

def update_alloc():
    total_wr = 0
    wr = {}

    for k in perf:
        t = perf[k]["win"] + perf[k]["loss"]
        if t == 0:
            wr[k] = 0.33
        else:
            wr[k] = perf[k]["win"] / t
        total_wr += wr[k]

    if total_wr == 0:
        return

    for k in alloc:
        alloc[k] = wr[k] / total_wr

print("AI TRADER V18 QUANT CALISIYOR...")
send("🧠 V18 AUTO PORTFOLIO AKTİF")

while True:
    try:
        update_alloc()

        candidates = []

        for symbol in symbols:
            df = get_data(symbol)
            if df is None:
                continue

            df["RSI"] = rsi(df)
            df["ATR"] = atr(df)
            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()

            price = float(df["Close"].iloc[-1])
            rsi_v = float(df["RSI"].iloc[-1])
            ma20 = float(df["MA20"].iloc[-1])
            ma50 = float(df["MA50"].iloc[-1])
            atr_v = float(df["ATR"].iloc[-1])
            momentum = float(df["Close"].iloc[-1] - df["Close"].iloc[-3])

            market_type = detect_market(df)

            trend_score = (price > ma20)*2 + (price > ma50)*2 + (momentum > 0)*2
            scalp_score = (rsi_v < 35)*3 + (momentum > -0.2)*2
            rev_score = (rsi_v < 30)*4 + (momentum > -0.5)*2

            if market_type == "trend":
                strategy, score = "trend", trend_score
            elif market_type == "down":
                strategy, score = "reversal", rev_score
            else:
                strategy, score = "scalp", scalp_score

            if score >= 5:
                candidates.append((symbol, price, atr_v, score, strategy))

        for c in sorted(candidates, key=lambda x: x[3], reverse=True):

            if len(active_trades) >= 2:
                break

            symbol, price, atr_v, score, strategy = c

            if any(t["symbol"] == symbol for t in active_trades):
                continue

            sl = price - atr_v * 1.5
            tp = price + atr_v * 3

            # 💣 STRATEGY BASED CAPITAL
            strat_cap = capital * alloc[strategy]
            risk_pct = 0.02

            risk_amount = strat_cap * risk_pct
            risk_per_share = price - sl

            if risk_per_share <= 0:
                continue

            lot = round(risk_amount / risk_per_share, 2)

            trade = {
                "symbol": symbol,
                "entry": price,
                "tp": tp,
                "sl": sl,
                "strategy": strategy,
                "lot": lot
            }

            active_trades.append(trade)

            send(f"🚀 V18 TRADE {symbol}\nStrat:{strategy}\nLot:{lot}")

        for t in active_trades[:]:
            df = get_data(t["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price >= t["tp"]:
                perf[t["strategy"]]["win"] += 1
                send(f"🟢 WIN {t['symbol']} ({t['strategy']})")
                active_trades.remove(t)

            elif price <= t["sl"]:
                perf[t["strategy"]]["loss"] += 1
                send(f"🔴 LOSS {t['symbol']} ({t['strategy']})")
                active_trades.remove(t)

        save_all()

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)
