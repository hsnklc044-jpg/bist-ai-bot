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

print("AI TRADER V15 FINAL CALISIYOR...")
send("🧠 V15 CAPITAL + V14.1 AKTİF")

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

            trend_score = 0
            if price > ma20: trend_score += 2
            if price > ma50: trend_score += 2
            if momentum > 0: trend_score += 2

            scalp_score = 0
            if rsi_v < 35: scalp_score += 3
            if momentum > -0.2: scalp_score += 2

            rev_score = 0
            if rsi_v < 30: rev_score += 4
            if momentum > -0.5: rev_score += 2

            best_score = max(trend_score, scalp_score, rev_score)

            if best_score >= 5:
                candidates.append((symbol, price, atr_v, best_score))

        for c in sorted(candidates, key=lambda x: x[3], reverse=True):
            if len(active_trades) >= MAX_TRADES:
                break

            if any(t["symbol"] == c[0] for t in active_trades):
                continue

            symbol = c[0]
            price = c[1]
            atr_v = c[2]
            score = c[3]

            sl = round(price - atr_v * 1.5, 2)
            tp = round(price + atr_v * 3, 2)

            # 💣 SCORE BASED RISK
            if score >= 7:
                risk_pct = 0.03
            elif score == 6:
                risk_pct = 0.02
            else:
                risk_pct = 0.01

            risk_amount = capital * risk_pct
            risk_per_share = price - sl

            if risk_per_share <= 0:
                continue

            lot = round(risk_amount / risk_per_share, 2)

            trade = {
                "symbol": symbol,
                "entry": price,
                "tp": tp,
                "sl": sl,
                "score": score,
                "lot": lot
            }

            active_trades.append(trade)

            send(f"🚀 V15 TRADE {symbol}\nScore:{score}\nLot:{lot}\nEntry:{round(price,2)} TP:{tp} SL:{sl}")

        for t in active_trades[:]:
            df = get_data(t["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price >= t["tp"]:
                profit = (t["tp"] - t["entry"]) * t["lot"]
                capital += profit
                send(f"🟢 WIN {t['symbol']} +{round(profit,2)}")
                active_trades.remove(t)

            elif price <= t["sl"]:
                loss = (t["entry"] - t["sl"]) * t["lot"]
                capital -= loss
                send(f"🔴 LOSS {t['symbol']} -{round(loss,2)}")
                active_trades.remove(t)

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)
