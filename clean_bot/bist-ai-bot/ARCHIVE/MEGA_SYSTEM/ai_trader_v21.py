import requests
import time
import yfinance as yf
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"
url = "https://api.telegram.org/bot" + TOKEN

symbols = ["THYAO","YKBNK","AKBNK","BIMAS","EREGL"]

active_trades = []

capital = 100000
wins = 0
losses = 0
total_profit = 0

strategy_stats = {
    "trend":{"win":0,"loss":0},
    "scalp":{"win":0,"loss":0},
    "reversal":{"win":0,"loss":0}
}

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

print("AI TRADER V21 PERFORMANCE AI CALISIYOR...")
send("🧠 V21 PERFORMANCE AI AKTİF")

while True:
    try:

        for symbol in symbols:
            df = get_data(symbol)
            if df is None:
                continue

            df["RSI"] = rsi(df)
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

            lot = 1000

            trade = {
                "symbol": symbol,
                "entry": price,
                "tp": tp,
                "sl": sl,
                "strategy":"trend",
                "lot": lot
            }

            active_trades.append(trade)

            send(f"🚀 V21 TRADE {symbol}")

        for t in active_trades[:]:
            df = get_data(t["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price >= t["tp"]:
                profit = (t["tp"] - t["entry"]) * t["lot"]
                capital += profit
                wins += 1
                total_profit += profit
                strategy_stats[t["strategy"]]["win"] += 1
                active_trades.remove(t)

            elif price <= t["sl"]:
                loss = (t["entry"] - t["sl"]) * t["lot"]
                capital -= loss
                losses += 1
                total_profit -= loss
                strategy_stats[t["strategy"]]["loss"] += 1
                active_trades.remove(t)

        total = wins + losses

        if total > 0:
            winrate = round((wins / total) * 100, 2)

            best = max(strategy_stats, key=lambda x: strategy_stats[x]["win"])
            worst = min(strategy_stats, key=lambda x: strategy_stats[x]["win"])

            send(f"📊 SYSTEM REPORT\nWin:{wins} Loss:{losses}\nWinrate:{winrate}%\nProfit:{round(total_profit,2)}\nBest:{best}\nWorst:{worst}")

    except Exception as e:
        print("HATA:", e)

    time.sleep(300)
