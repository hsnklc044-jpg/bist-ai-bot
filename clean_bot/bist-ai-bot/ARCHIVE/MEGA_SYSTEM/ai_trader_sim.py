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

capital = 100000  # 🔥 sanal para
peak_capital = capital

active_trades = []
COOLDOWN = {}

wins = 0
losses = 0
total_profit = 0

RISK_PER_TRADE = 0.02
MAX_DRAWDOWN = 0.15
MAX_TRADES = 2

def send(msg):
    try:
        requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def log_trade(text):
    with open("trade_log.txt","a",encoding="utf-8") as f:
        f.write(text + "\n")

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

print("AI TRADER V10.1 SIMULATION CALISIYOR...")
send("🧠 AI TRADER SIMULATION AKTİF")

while True:
    try:
        now = datetime.now()

        if now.hour < 10 or now.hour > 18:
            time.sleep(60)
            continue

        dd = (peak_capital - capital) / peak_capital
        if dd >= MAX_DRAWDOWN:
            send("⛔ SIM STOP (DD)")
            break

        candidates = []

        for symbol in symbols:

            if symbol in COOLDOWN and (time.time() - COOLDOWN[symbol]) < 1200:
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

            momentum = float(df["Close"].iloc[-1] - df["Close"].iloc[-3])

            if momentum < -0.5:
                continue

            if ma20 < ma50 * 0.98:
                continue

            if rsi_v < 20:
                continue

            score = 0

            if rsi_v < 30: score += 4
            elif rsi_v < 40: score += 3
            elif rsi_v < 55: score += 2

            if price > ma20: score += 2
            if price > ma50: score += 1

            if atr_v / price > 0.08:
                continue

            if score >= 5:
                candidates.append((symbol, price, atr_v, score))

        if len(candidates) == 0:
            send("⚖️ Sim: Trade yok")

        for c in sorted(candidates, key=lambda x: x[3], reverse=True):

            if len(active_trades) >= MAX_TRADES:
                break

            if any(t["symbol"] == c[0] for t in active_trades):
                continue

            price = c[1]
            atr_v = c[2]

            sl = round(price - atr_v * 1.4, 2)
            tp = round(price + atr_v * 3.5, 2)

            risk_amount = capital * RISK_PER_TRADE
            risk_per_share = price - sl

            if risk_per_share <= 0:
                continue

            lot = round(risk_amount / risk_per_share, 2)

            trade = {
                "symbol": c[0],
                "entry": price,
                "tp": tp,
                "sl": sl,
                "lot": lot,
                "max": price
            }

            active_trades.append(trade)

            send(f"🚀 SIM TRADE\n{trade['symbol']}\nEntry:{round(price,2)} Lot:{lot}")

        for t in active_trades[:]:
            df = get_data(t["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price >= t["tp"]:
                profit = (t["tp"] - t["entry"]) * t["lot"]
                capital += profit
                total_profit += profit
                wins += 1
                send(f"🟢 SIM TP {t['symbol']} +{round(profit,2)}")
                active_trades.remove(t)

            elif price <= t["sl"]:
                loss = (t["entry"] - t["sl"]) * t["lot"]
                capital -= loss
                total_profit -= loss
                losses += 1
                send(f"🔴 SIM SL {t['symbol']} -{round(loss,2)}")
                active_trades.remove(t)

        total = wins + losses
        if total > 0:
            winrate = round((wins / total) * 100, 2)
            send(f"📊 SIM DURUM\nBakiye:{round(capital,2)}\nKar:{round(total_profit,2)}\nWin:{wins} Loss:{losses}\nBaşarı:{winrate}%")

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)
