import requests
import time
import numpy as np
import pandas as pd
from binance.client import Client

# 🔑 Binance
client = Client()

# 🔑 TELEGRAM
TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Telegram HATA:", e)

symbols = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

def signal(symbol):
    try:
        klines = client.get_klines(symbol=symbol, interval="5m", limit=100)

        closes = [float(k[4]) for k in klines]
        volumes = [float(k[5]) for k in klines]

        price = closes[-1]

        # RSI
        delta = np.diff(closes)
        gain = np.maximum(delta, 0)
        loss = -np.minimum(delta, 0)

        avg_gain = np.mean(gain[-14:])
        avg_loss = np.mean(loss[-14:]) + 1e-9
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # EMA
        ema20 = pd.Series(closes).ewm(span=20).mean().iloc[-1]
        ema50 = pd.Series(closes).ewm(span=50).mean().iloc[-1]

        trend = ema20 > ema50

        # Momentum
        mom = closes[-1] > closes[-5]

        # Volume
        vol = volumes[-1] > np.mean(volumes[-20:])

        # Score
        score = 0
        if trend: score += 20
        if mom: score += 20
        if vol: score += 20
        if rsi < 30 or rsi > 70: score += 20

        print(f"{symbol} Score:{score} Trend:{trend} Mom:{mom} Vol:{vol}")

        # 🔥 KESİN PRO FİLTRE (BLOKLAYICI)
        if not (score >= 60 and trend and mom and vol):
            return

        direction = "LONG" if trend else "SHORT"

        send(f"""
🚀 V72 PRO SIGNAL

Symbol: {symbol}
Direction: {direction}
Price: {price}

Score: {score}
RSI: {rsi:.2f}

Trend: {trend}
Momentum: {mom}
Volume: {vol}
""")

    except Exception as e:
        print("HATA:", e)


def run():
    while True:
        try:
            for s in symbols:
                signal(s)
                time.sleep(1)
            time.sleep(20)
        except Exception as e:
            print("HATA:", e)
            time.sleep(5)


if __name__ == "__main__":
    send("🚀 V72 PRO ENGINE AKTİF")
    run()
