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
peak_capital = 100000

loss_streak = 0
MAX_LOSS_STREAK = 3
MAX_DRAWDOWN = 0.05

paused = False

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

print("AI TRADER V20 RISK CONTROL CALISIYOR...")
send("🧠 V20 FULL RISK CONTROL AKTİF")

while True:
    try:

        # 💣 DRAWDOWN KONTROL
        if capital > peak_capital:
            peak_capital = capital

        drawdown = (peak_capital - capital) / peak_capital

        if drawdown >= MAX_DRAWDOWN:
            paused = True
            send("⛔ MAX DRAWDOWN - SYSTEM PAUSED")

        if loss_streak >= MAX_LOSS_STREAK:
            paused = True
            send("⚠️ LOSS STREAK - SYSTEM PAUSED")

        if paused:
            time.sleep(300)
            continue

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

            risk_pct = 0.02
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
                "lot": lot
            }

            active_trades.append(trade)

            send(f"🚀 V20 TRADE {symbol}\nLot:{lot}")

        for t in active_trades[:]:
            df = get_data(t["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price >= t["tp"]:
                profit = (t["tp"] - t["entry"]) * t["lot"]
                capital += profit
                loss_streak = 0
                send(f"🟢 WIN {t['symbol']} +{round(profit,2)}")
                active_trades.remove(t)

            elif price <= t["sl"]:
                loss = (t["entry"] - t["sl"]) * t["lot"]
                capital -= loss
                loss_streak += 1
                send(f"🔴 LOSS {t['symbol']} -{round(loss,2)}")
                active_trades.remove(t)

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)
