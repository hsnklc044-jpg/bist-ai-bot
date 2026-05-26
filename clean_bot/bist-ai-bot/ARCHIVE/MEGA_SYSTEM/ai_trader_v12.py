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

sectors = {
    "YKBNK":"BANK",
    "AKBNK":"BANK",
    "GARAN":"BANK",
    "ISCTR":"BANK",
    "THYAO":"AVIATION",
    "BIMAS":"RETAIL",
    "EREGL":"INDUSTRY"
}

capital = 100000
active_trades = []

RISK_PER_TRADE = 0.02
MAX_TOTAL_RISK = 0.04
MAX_TRADES = 2

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

print("AI TRADER V12 ELITE CALISIYOR...")
send("🧠 V12 ELITE AKTİF")

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

        # 🔥 en iyi trade'leri seç
        candidates = sorted(candidates, key=lambda x: x[3], reverse=True)

        used_sectors = [sectors[t["symbol"]] for t in active_trades]

        total_risk = len(active_trades) * RISK_PER_TRADE

        for c in candidates:

            if len(active_trades) >= MAX_TRADES:
                break

            if total_risk >= MAX_TOTAL_RISK:
                break

            symbol = c[0]
            sector = sectors.get(symbol,"OTHER")

            if sector in used_sectors:
                continue

            price = c[1]
            atr_v = c[2]

            sl = price - atr_v * 1.5
            tp = price + atr_v * 3

            lot = (capital * RISK_PER_TRADE) / (price - sl)

            trade = {
                "symbol": symbol,
                "entry": price,
                "tp": tp,
                "sl": sl,
                "lot": lot
            }

            active_trades.append(trade)
            used_sectors.append(sector)
            total_risk += RISK_PER_TRADE

            send(f"🚀 ELITE TRADE {symbol} Score:{c[3]}")

        for t in active_trades[:]:
            df = get_data(t["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price >= t["tp"]:
                send(f"🟢 WIN {t['symbol']}")
                active_trades.remove(t)

            elif price <= t["sl"]:
                send(f"🔴 LOSS {t['symbol']}")
                active_trades.remove(t)

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)
