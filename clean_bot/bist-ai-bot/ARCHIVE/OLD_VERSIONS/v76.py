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

        trend_up = price > avg
        trend_down = price < avg

        mom_up = closes[-1] > closes[-2]
        mom_down = closes[-1] < closes[-2]

        score = 0
        if trend_up or trend_down:
            score += 20
        if mom_up or mom_down:
            score += 20

        if score < 40:
            return

        if trend_up and mom_up:
            direction = "LONG"
        elif trend_down and mom_down:
            direction = "SHORT"
        else:
            return

        key = f"{symbol}_{direction}"

        if key in last_signals:
            last_price = last_signals[key]
            if abs(price - last_price) / price < 0.002:
                return

        last_signals[key] = price

        if direction == "LONG":
            tp = price * 1.01
            sl = price * 0.995
        else:
            tp = price * 0.99
            sl = price * 1.005

        msg = f"""🚀 V76 TRADE SIGNAL

Symbol: {symbol}
Direction: {direction}

Entry: {round(price,2)}
TP: {round(tp,2)}
SL: {round(sl,2)}

Score: {score}
Risk: %1
"""

        send(msg)

    except Exception as e:
        print("HATA:", e)


def run():
    print("V76 STARTED")

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
    send("🚀 V76 TRADE ENGINE AKTİF")
    run()
