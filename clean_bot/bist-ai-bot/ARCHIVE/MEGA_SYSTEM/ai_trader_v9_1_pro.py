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
bank_symbols = ["YKBNK","AKBNK","GARAN","ISCTR"]

capital = 100000
peak_capital = capital

active_trades = []
COOLDOWN = {}

RISK_PER_TRADE = 0.02
MAX_DRAWDOWN = 0.15
MAX_TRADES = 3

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

print("AI TRADER V9.1 PRO CALISIYOR...")
send("🧠 AI TRADER V9.1 PRO AKTİF")

while True:
    try:
        now = datetime.now()

        if now.hour < 10 or now.hour > 18:
            time.sleep(60)
            continue

        dd = (peak_capital - capital) / peak_capital
        if dd >= MAX_DRAWDOWN:
            send("⛔ MAX DD STOP")
            break

        candidates = []

        for symbol in symbols:

            if symbol in COOLDOWN and (time.time() - COOLDOWN[symbol]) < 1800:
                continue

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

            # 🔥 MOMENTUM
            momentum = float(df["Close"].iloc[-1] - df["Close"].iloc[-5])

            if momentum <= 0:
                continue

            if ma20 < ma50:
                continue

            if rsi_v < 25:
                continue

            score = 0

            if rsi_v < 30: score += 4
            elif rsi_v < 40: score += 3
            elif rsi_v < 50: score += 2

            if price > ma20: score += 2
            if price > ma50: score += 1

            if atr_v / price > 0.06:
                continue

            if score >= 5:
                candidates.append((symbol, price, atr_v, score))

        if len(candidates) == 0:
            send("⚖️ Uygun trade yok")

        for c in sorted(candidates, key=lambda x: x[3], reverse=True):

            if len(active_trades) >= MAX_TRADES:
                break

            if any(t["symbol"] == c[0] for t in active_trades):
                continue

            if c[0] in bank_symbols:
                if sum(1 for t in active_trades if t["symbol"] in bank_symbols) >= 1:
                    continue

            price = c[1]
            atr_v = c[2]

            sl = round(price - atr_v * 1.5, 2)
            tp = round(price + atr_v * 3.5, 2)

            risk_amount = capital * RISK_PER_TRADE
            risk_per_share = price - sl

            if risk_per_share <= 0:
                continue

            lot = round(risk_amount / risk_per_share, 2)

            # 🔥 LOT LIMIT
            lot = min(lot, round((capital * 0.3) / price, 2))

            trade = {
                "symbol": c[0],
                "entry": price,
                "tp": tp,
                "sl": sl,
                "lot": lot,
                "max": price
            }

            active_trades.append(trade)

            send(f"🚀 TRADE\n{trade['symbol']}\nEntry:{round(price,2)}\nLot:{lot}\nTP:{tp} SL:{sl}")

        for t in active_trades[:]:
            df = get_data(t["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price > t["max"]:
                t["max"] = price

            if t["max"] > t["entry"] * 1.02:
                new_sl = t["max"] * 0.985
                if new_sl > t["sl"]:
                    t["sl"] = new_sl
                    send(f"🔄 SL Update {t['symbol']} → {round(t['sl'],2)}")

            if price >= t["tp"]:
                profit = (t["tp"] - t["entry"]) * t["lot"]
                capital += profit
                peak_capital = max(peak_capital, capital)
                send(f"🟢 TP {t['symbol']} +{round(profit,2)}")
                COOLDOWN[t["symbol"]] = time.time()
                active_trades.remove(t)

            elif price <= t["sl"]:
                loss = (t["entry"] - t["sl"]) * t["lot"]
                capital -= loss
                send(f"🔴 SL {t['symbol']} -{round(loss,2)}")
                COOLDOWN[t["symbol"]] = time.time()
                active_trades.remove(t)

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)
