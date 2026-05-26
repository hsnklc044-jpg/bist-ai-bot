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

# 💰 RİSK AYARI
BALANCE = 1000      # hesap büyüklüğü (USD)
RISK_PERCENT = 1    # %1 risk

def signal(symbol):
    try:
        klines = client.get_klines(symbol=symbol, interval="5m", limit=100)

        closes = [float(k[4]) for k in klines]
        highs = [float(k[2]) for k in klines]
        lows = [float(k[3]) for k in klines]
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

        # ATR (basit)
        tr = [highs[i] - lows[i] for i in range(len(highs))]
        atr = np.mean(tr[-14:])

        # Score
        score = 0
        if trend: score += 20
        if mom: score += 20
        if vol: score += 20
        if rsi < 30 or rsi > 70: score += 20

        print(f"{symbol} Score:{score} Trend:{trend} Mom:{mom} Vol:{vol}")

        # 🔥 PRO FİLTRE
        if not (score >= 60 and trend and mom and vol):
            return

        # 🎯 DIRECTION
        direction = "LONG" if trend else "SHORT"

        # 🎯 TP / SL (ATR bazlı)
        if direction == "LONG":
            sl = price - atr
            tp = price + (atr * 2)
        else:
            sl = price + atr
            tp = price - (atr * 2)

        # 💰 RİSK HESAP
        risk_amount = BALANCE * (RISK_PERCENT / 100)
        qty = risk_amount / abs(price - sl)

        send(f"""
🚀 V73 TRADE SIGNAL

Symbol: {symbol}
Direction: {direction}

Entry: {price:.2f}
TP: {tp:.2f}
SL: {sl:.2f}

Risk: %{RISK_PERCENT}
Qty: {qty:.4f}

Score: {score}
RSI: {rsi:.2f}
ATR: {atr:.4f}
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
    send("🚀 V73 TRADE ENGINE AKTİF")
    run()
