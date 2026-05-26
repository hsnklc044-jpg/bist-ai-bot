import requests
import time
import numpy as np
import pandas as pd
from binance.client import Client

client = Client()

TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

symbols = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

BALANCE = 1000
RISK_PERCENT = 1

open_trades = {}

def signal(symbol):
    try:
        if symbol in open_trades:
            return

        klines = client.get_klines(symbol=symbol, interval="5m", limit=100)

        closes = [float(k[4]) for k in klines]
        highs = [float(k[2]) for k in klines]
        lows = [float(k[3]) for k in klines]
        volumes = [float(k[5]) for k in klines]

        price = closes[-1]

        ema20 = pd.Series(closes).ewm(span=20).mean().iloc[-1]
        ema50 = pd.Series(closes).ewm(span=50).mean().iloc[-1]

        trend = ema20 > ema50
        mom = closes[-1] > closes[-5]
        vol = volumes[-1] > np.mean(volumes[-20:])

        tr = [highs[i] - lows[i] for i in range(len(highs))]
        atr = np.mean(tr[-14:])

        score = 0
        if trend: score += 20
        if mom: score += 20
        if vol: score += 20

        if not (score >= 40 and trend):
            return

        direction = "LONG"

        sl = price - atr
        tp = price + (atr * 2)

        risk_amount = BALANCE * (RISK_PERCENT / 100)
        qty = risk_amount / abs(price - sl)

        open_trades[symbol] = {
            "entry": price,
            "sl": sl,
            "tp": tp,
            "direction": direction,
            "qty": qty,
            "be": False
        }

        send(f"""
🚀 V74 TRADE OPEN

{symbol}
Entry: {price:.2f}
TP: {tp:.2f}
SL: {sl:.2f}
Qty: {qty:.4f}
""")

    except Exception as e:
        print("HATA:", e)


def manage_trades():
    for symbol in list(open_trades.keys()):
        try:
            trade = open_trades[symbol]
            price = float(client.get_symbol_ticker(symbol=symbol)['price'])

            entry = trade["entry"]
            sl = trade["sl"]
            tp = trade["tp"]

            # ❌ STOP LOSS
            if price <= sl:
                send(f"❌ SL HIT {symbol} @ {price}")
                del open_trades[symbol]
                continue

            # 🎯 TAKE PROFIT
            if price >= tp:
                send(f"✅ TP HIT {symbol} @ {price}")
                del open_trades[symbol]
                continue

            # 🔄 BREAK EVEN
            if not trade["be"] and price >= entry + (tp - entry)/2:
                trade["sl"] = entry
                trade["be"] = True
                send(f"🔄 BE SET {symbol}")

            # 📈 TRAILING
            if trade["be"]:
                new_sl = price - (tp - entry)/3
                if new_sl > trade["sl"]:
                    trade["sl"] = new_sl

        except Exception as e:
            print("Manage HATA:", e)


def run():
    while True:
        try:
            for s in symbols:
                signal(s)
                time.sleep(1)

            manage_trades()

            time.sleep(20)

        except Exception as e:
            print("HATA:", e)
            time.sleep(5)


if __name__ == "__main__":
    send("🚀 V74 ADVANCED ENGINE AKTİF")
    run()
