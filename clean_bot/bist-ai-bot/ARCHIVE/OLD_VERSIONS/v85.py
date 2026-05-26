import time
import requests

symbols = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

last_signal = None
last_time = 0
COOLDOWN = 180

# ---------------- TELEGRAM ----------------
def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=5)
    except Exception as e:
        print("Telegram error:", e)

# ---------------- DATA ----------------
def get_data(symbol, interval="5m"):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=120"
    try:
        return requests.get(url, timeout=5).json()
    except:
        return None

# ---------------- EMA ----------------
def ema(data, period=20):
    k = 2 / (period + 1)
    ema_vals = [data[0]]
    for price in data[1:]:
        ema_vals.append(price * k + ema_vals[-1] * (1 - k))
    return ema_vals

# ---------------- RSI ----------------
def rsi(closes, period=14):
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        if diff > 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    avg_gain = sum(gains[-period:]) / period if gains else 0.0001
    avg_loss = sum(losses[-period:]) / period if losses else 0.0001

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ---------------- BTC MARKET FILTER ----------------
def btc_trend():
    data = get_data("BTCUSDT", "15m")
    if not data:
        return None

    closes = [float(x[4]) for x in data]
    ema20 = ema(closes, 20)

    if closes[-1] > ema20[-1] and ema20[-1] > ema20[-3]:
        return "UP"
    elif closes[-1] < ema20[-1] and ema20[-1] < ema20[-3]:
        return "DOWN"
    else:
        return "SIDE"

# ---------------- FAKE BREAKOUT ----------------
def fake_breakout(closes):
    last3 = closes[-3:]
    move = max(last3) - min(last3)
    return move / closes[-1] > 0.012

# ---------------- ANALYZE ----------------
def analyze(symbol, btc_direction):
    data5 = get_data(symbol, "5m")
    data15 = get_data(symbol, "15m")

    if not data5 or not data15:
        return None

    try:
        closes5 = [float(x[4]) for x in data5]
        volumes5 = [float(x[5]) for x in data5]

        closes15 = [float(x[4]) for x in data15]

        price = closes5[-1]

        ema5 = ema(closes5, 20)
        ema15 = ema(closes15, 20)

        rsi_val = rsi(closes5)

        vol_avg = sum(volumes5[-15:]) / 15
        vol_ok = volumes5[-1] > vol_avg * 1.1

        trend5_up = price > ema5[-1] and ema5[-1] > ema5[-3]
        trend5_down = price < ema5[-1] and ema5[-1] < ema5[-3]

        trend15_up = closes15[-1] > ema15[-1]
        trend15_down = closes15[-1] < ema15[-1]

        mom_up = closes5[-1] > closes5[-2]
        mom_down = closes5[-1] < closes5[-2]

        if fake_breakout(closes5):
            return None

        score = 0
        if trend5_up or trend5_down: score += 25
        if trend15_up or trend15_down: score += 20
        if vol_ok: score += 25
        if 45 < rsi_val < 65: score += 20
        if mom_up or mom_down: score += 10

        if score < 70:
            return None

        # 🎯 MARKET FILTER
        if btc_direction == "UP":
            if not (trend5_up and trend15_up and mom_up and 50 < rsi_val < 65):
                return None
            direction = "LONG"

        elif btc_direction == "DOWN":
            if not (trend5_down and trend15_down and mom_down and 35 < rsi_val < 50):
                return None
            direction = "SHORT"

        else:
            return None

        return {
            "symbol": symbol,
            "price": price,
            "score": score,
            "direction": direction,
            "rsi": rsi_val,
            "btc": btc_direction
        }

    except Exception as e:
        print("Analyze error:", e)
        return None

# ---------------- MAIN ----------------
def run():
    global last_signal, last_time

    print("V85 ELITE STARTED")

    while True:
        try:
            btc_direction = btc_trend()

            if btc_direction == "SIDE" or btc_direction is None:
                print("MARKET SIDEWAYS - NO TRADE")
                time.sleep(10)
                continue

            best = None

            for s in symbols:
                result = analyze(s, btc_direction)
                if result:
                    if not best or result["score"] > best["score"]:
                        best = result
                time.sleep(0.3)

            if best:
                key = f'{best["symbol"]}_{best["direction"]}'
                now = time.time()

                if key != last_signal and (now - last_time > COOLDOWN):
                    last_signal = key
                    last_time = now

                    price = best["price"]

                    if best["direction"] == "LONG":
                        tp = price * 1.015
                        sl = price * 0.993
                    else:
                        tp = price * 0.985
                        sl = price * 1.007

                    msg = f"""🚀 V85 ELITE SIGNAL

Symbol: {best["symbol"]}
Direction: {best["direction"]}

Entry: {round(price,2)}
TP: {round(tp,2)}
SL: {round(sl,2)}

Score: {best["score"]}
RSI: {round(best["rsi"],2)}
BTC Trend: {best["btc"]}
"""

                    print("SIGNAL:", best)
                    send(msg)

            time.sleep(5)

        except Exception as e:
            print("Loop error:", e)
            time.sleep(5)

# ---------------- START ----------------
if __name__ == "__main__":
    send("🚀 V85 ELITE AKTİF")
    run()