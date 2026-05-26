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

# 🔥 STRATEJİ PERFORMANSI (öğrenme)
perf_file = "strategy_perf.json"

default_perf = {
    "trend": {"win":0,"loss":0},
    "scalp": {"win":0,"loss":0},
    "reversal": {"win":0,"loss":0}
}

try:
    with open(perf_file,"r") as f:
        perf = json.load(f)
except:
    perf = default_perf

def save_perf():
    with open(perf_file,"w") as f:
        json.dump(perf,f)

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

# 💣 MARKET REGIME DETECTOR
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

print("AI TRADER V17 ADAPTIVE SIM CALISIYOR...")
send("🧠 V17 ADAPTIVE AI (SIM MODE) AKTİF")

while True:
    try:
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

            # 🧠 STRATEJİLER
            trend_score = (price > ma20)*2 + (price > ma50)*2 + (momentum > 0)*2
            scalp_score = (rsi_v < 35)*3 + (momentum > -0.2)*2
            rev_score = (rsi_v < 30)*4 + (momentum > -0.5)*2

            # 💣 ADAPTIVE SEÇİM
            if market_type == "trend":
                best = ("trend", trend_score)
            elif market_type == "down":
                best = ("reversal", rev_score)
            else:
                best = ("scalp", scalp_score)

            strategy, score = best

            # 🔥 performansa göre boost
            total = perf[strategy]["win"] + perf[strategy]["loss"]
            if total > 5:
                winrate = perf[strategy]["win"] / total
                score += int(winrate * 2)

            if score >= 5:
                candidates.append((symbol, price, atr_v, score, strategy))

        for c in sorted(candidates, key=lambda x: x[3], reverse=True):

            if len(active_trades) >= 2:
                break

            if any(t["symbol"] == c[0] for t in active_trades):
                continue

            symbol, price, atr_v, score, strategy = c

            sl = round(price - atr_v * 1.5, 2)
            tp = round(price + atr_v * 3, 2)

            trade = {
                "symbol": symbol,
                "entry": price,
                "tp": tp,
                "sl": sl,
                "strategy": strategy
            }

            active_trades.append(trade)

            mode = "SIM" if SIM_MODE else "REAL"
            send(f"🚀 V17 {mode} TRADE {symbol}\nStrat:{strategy}\nScore:{score}")

        # 🔥 TRADE TAKİP
        for t in active_trades[:]:
            df = get_data(t["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price >= t["tp"]:
                perf[t["strategy"]]["win"] += 1
                save_perf()
                send(f"🟢 WIN {t['symbol']} ({t['strategy']})")
                active_trades.remove(t)

            elif price <= t["sl"]:
                perf[t["strategy"]]["loss"] += 1
                save_perf()
                send(f"🔴 LOSS {t['symbol']} ({t['strategy']})")
                active_trades.remove(t)

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)
