import requests
import time
import yfinance as yf
import pandas as pd
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"

url = "https://api.telegram.org/bot" + TOKEN

symbols = ["THYAO","YKBNK","AKBNK","BIMAS","EREGL"]

active_trades = []
wins = 0
losses = 0

MAX_TRADES = 3
RISK_PERCENT = 0.03
TRAIL_TRIGGER = 0.02
TRAIL_GAP = 0.015
MAX_DAILY_LOSS = 5  # %

daily_loss = 0
last_day = datetime.now().day

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

def rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

print("AI TRADER V6 CALISIYOR...")
send("💼 AI TRADER V6 AKTİF")

while True:
    try:
        # 🗓 Gün reset
        if datetime.now().day != last_day:
            daily_loss = 0
            last_day = datetime.now().day
            send("🗓 Yeni gün başladı")

        # ❌ Günlük risk limiti
        if daily_loss >= MAX_DAILY_LOSS:
            send("⛔ Günlük risk limiti doldu")
            time.sleep(300)
            continue

        candidates = []

        # 📊 TARAYICI
        for symbol in symbols:
            df = get_data(symbol)
            if df is None:
                continue

            df["RSI"] = rsi(df)
            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()

            price = float(df["Close"].iloc[-1])
            rsi_val = float(df["RSI"].iloc[-1])
            ma20 = float(df["MA20"].iloc[-1])
            ma50 = float(df["MA50"].iloc[-1])

            score = 0

            if rsi_val < 30: score += 4
            elif rsi_val < 40: score += 3
            elif rsi_val < 50: score += 2

            if price > ma20: score += 2
            if price > ma50: score += 1

            tp = round(price * 1.05, 2)
            sl = round(price * (1 - RISK_PERCENT), 2)

            if score >= 4:
                candidates.append((symbol, price, rsi_val, score, tp, sl))

        # 🔥 EN İYİLERİ SIRALA
        candidates = sorted(candidates, key=lambda x: x[3], reverse=True)

        # 🚀 TRADE AÇ
        for c in candidates:
            if len(active_trades) >= MAX_TRADES:
                break

            already = any(t["symbol"] == c[0] for t in active_trades)
            if already:
                continue

            trade = {
                "symbol": c[0],
                "entry": c[1],
                "tp": c[4],
                "sl": c[5],
                "max_price": c[1]
            }

            active_trades.append(trade)

            send(f"🚀 TRADE\n{trade['symbol']}\nEntry:{trade['entry']}\nTP:{trade['tp']} SL:{trade['sl']}")

        # 🔄 TAKİP
        for trade in active_trades[:]:
            df = get_data(trade["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price > trade["max_price"]:
                trade["max_price"] = price

            # 🔄 TRAILING
            if trade["max_price"] >= trade["entry"] * (1 + TRAIL_TRIGGER):
                new_sl = round(trade["max_price"] * (1 - TRAIL_GAP), 2)
                if new_sl > trade["sl"]:
                    trade["sl"] = new_sl
                    send(f"🔄 SL Güncellendi {trade['symbol']} → {trade['sl']}")

            # 🟢 TP
            if price >= trade["tp"]:
                wins += 1
                send(f"🟢 TP {trade['symbol']}")
                active_trades.remove(trade)

            # 🔴 SL
            elif price <= trade["sl"]:
                losses += 1
                daily_loss += 3
                send(f"🔴 SL {trade['symbol']}")
                active_trades.remove(trade)

        # 📊 RAPOR
        total = wins + losses
        if total > 0:
            winrate = round((wins / total) * 100, 2)
            send(f"📊 PORTFÖY\nWin:{wins} Loss:{losses}\nBaşarı:{winrate}%")

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)
