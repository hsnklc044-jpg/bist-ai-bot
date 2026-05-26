import time
import requests

symbols = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

last_signals = {}

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("TELEGRAM HATA:", e)

def get_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=50"
    return requests.get(url).json()

def signal(symbol):
    try:
        data = get_data(symbol)
        closes = [float(x[4]) for x in data]

        price = closes[-1]
        avg = sum(closes[-10:]) / 10

        trend = price > avg
        mom = closes[-1] > closes[-2]
        vol = True

        score = 0
        if trend:
            score += 20
        if mom:
            score += 20
        if vol:
            score += 20

        if not (score >= 40 and trend):
            return

        direction = "LONG"

        key = f"{symbol}_{direction}"

        if key in last_signals:
            last_price = last_signals[key]
            if abs(price - last_price) / price < 0.002:
                return

        last_signals[key] = price

        msg = f"""🚀 V75 SIGNAL

Symbol: {symbol}
Direction: {direction}
Price: {price}

Score: {score}
"""

        send(msg)

    except Exception as e:
        print("HATA:", e)

def run():
    print("V75 STARTED")

    while True:
        try:
            for s in symbols:
                signal(s)
                time.sleep(1)

            time.sleep(5)

        except Exception as e:
            print("HATA:", e)
            time.sleep(5)

if __name__ == "__main__":
    send("🚀 V75 PRO ENGINE AKTİF")
    run()