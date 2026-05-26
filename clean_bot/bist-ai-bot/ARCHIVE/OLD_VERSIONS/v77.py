import time
import requests

symbols = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

last_signal = None

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("TELEGRAM HATA:", e)


def get_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=50"
    return requests.get(url).json()


def analyze(symbol):
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
            return None

        if trend_up and mom_up:
            direction = "LONG"
        elif trend_down and mom_down:
            direction = "SHORT"
        else:
            return None

        return {
            "symbol": symbol,
            "price": price,
            "score": score,
            "direction": direction
        }

    except:
        return None


def run():
    global last_signal

    print("V77 STARTED")

    while True:
        try:
            best = None

            for s in symbols:
                result = analyze(s)
                if result:
                    if not best or result["score"] > best["score"]:
                        best = result

                time.sleep(1)

            if best:
                key = f'{best["symbol"]}_{best["direction"]}'

                if key != last_signal:
                    last_signal = key

                    price = best["price"]

                    if best["direction"] == "LONG":
                        tp = price * 1.01
                        sl = price * 0.995
                    else:
                        tp = price * 0.99
                        sl = price * 1.005

                    msg = f"""🚀 V77 BEST SIGNAL

Symbol: {best["symbol"]}
Direction: {best["direction"]}

Entry: {round(price,2)}
TP: {round(tp,2)}
SL: {round(sl,2)}

Score: {best["score"]}
Risk: %1
"""

                    send(msg)

            time.sleep(5)

        except Exception as e:
            print("HATA:", e)
            time.sleep(5)


if __name__ == "__main__":
    send("🚀 V77 ENGINE AKTİF")
    run()
