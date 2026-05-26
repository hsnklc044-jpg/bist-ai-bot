import time
import requests

symbols = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

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
    print("SIGNAL:", symbol)

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

        print(symbol, score, trend, mom, vol)

        if not (score >= 40 and trend):
            return

        msg = f"{symbol} SIGNAL | Price:{price} Score:{score}"
        send(msg)

    except Exception as e:
        print("HATA:", e)

def run():
    print("RUN STARTED")

    while True:
        try:
            for s in symbols:
                signal(s)
                time.sleep(1)

            time.sleep(2)

        except Exception as e:
            print("HATA:", e)
            time.sleep(5)

if __name__ == "__main__":
    print("SCRIPT STARTED")
    send("🚀 V74 AKTİF")
    run()