import requests
import time
import yfinance as yf
import pandas as pd
import numpy as np
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"
url = "https://api.telegram.org/bot" + TOKEN

symbols = ["THYAO","YKBNK","AKBNK","BIMAS","EREGL"]

performance = {s: {"win":0,"loss":0} for s in symbols}

capital = 100000
start_day_capital = capital

active_trades = []
COOLDOWN = {}

RISK_PER_TRADE = 0.02
MAX_TRADES = 2

daily_trades = 0

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

print("AI TRADER V11.2 CALISIYOR...")
send("🧠 V11.2 DISCIPLINE AKTİF")

while True:
    try:
        now = datetime.now()

        # günlük reset
        if now.hour == 10 and now.minute < 5:
            start_day_capital = capital
            daily_trades = 0

        # günlük risk kontrol
        change = (capital - start_day_capital) / start_day_capital

        if change <= -0.03:
            send("⛔ GÜNLÜK STOP")
            time.sleep(600)
            continue

        if change >= 0.05:
            send("🟢 GÜNLÜK KAR TAMAMLANDI")
            time.sleep(600)
            continue

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
            atr_v = float(df["ATR"].iloc[-1])
            ma20 = float(df["MA20"].iloc[-1])
            ma50 = float(df["MA50"].iloc[-1])

            momentum = float(df["Close"].iloc[-1] - df["Close"].iloc[-3])

            score = 0

            if rsi_v < 30: score += 4
            elif rsi_v < 40: score += 3

            if price > ma20: score += 2
            if price > ma50: score += 1

            if momentum > -0.2: score += 2

            if score >= 4:
                candidates.append((symbol, price, atr_v, score))

        for c in sorted(candidates, key=lambda x: x[3], reverse=True):

            if daily_trades >= 3:
                break

            if len(active_trades) >= MAX_TRADES:
                break

            price = c[1]
            atr_v = c[2]

            sl = price - atr_v * 1.5
            tp = price + atr_v * 3

            lot = (capital * RISK_PER_TRADE) / (price - sl)

            trade = {
                "symbol": c[0],
                "entry": price,
                "tp": tp,
                "sl": sl,
                "lot": lot
            }

            active_trades.append(trade)
            daily_trades += 1

            send(f"🚀 TRADE {trade['symbol']}")

        for t in active_trades[:]:
            df = get_data(t["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price >= t["tp"]:
                performance[t["symbol"]]["win"] += 1
                capital += (t["tp"] - t["entry"]) * t["lot"]
                send(f"🟢 WIN {t['symbol']}")
                active_trades.remove(t)

            elif price <= t["sl"]:
                performance[t["symbol"]]["loss"] += 1
                capital -= (t["entry"] - t["sl"]) * t["lot"]
                send(f"🔴 LOSS {t['symbol']}")
                active_trades.remove(t)

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)
