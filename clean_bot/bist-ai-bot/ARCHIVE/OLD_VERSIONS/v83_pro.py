import time
import requests

symbols = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

last_signal = None
last_time = 0
COOLDOWN = 90  # saniye

# ---------------- TELEGRAM ----------------
def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=5)
    except Exception as e:
        print("Telegram error:", e)

# ---------------- DATA ----------------
def get_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=100"
    for _ in range(3):
        try:
            return requests.get(url, timeout=5).json()
        except:
            time.sleep(1)
    return None

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

# ---------------- ANALYZE ----------------
def analyze(symbol):
    data = get_data(symbol)
    if not data:
        return None

    try:
        closes = [float(x[4]) for x in data]
        volumes = [float(x[5]) for x in data]

        price = closes[-1]
        avg = sum(closes[-10:]) / 10
        vol_avg = sum(volumes[-10:]) / 10
        rsi_val = rsi(closes)

        trend_up = price > avg
        trend_down = price < avg

        mom_up = closes[-1] > closes[-2]
        mom_down = closes[-1] < closes[-2]

        vol_ok = volumes[-1] > vol_avg

        # DEBUG
        print(f"{symbol} | RSI:{round(rsi_val,2)} | Up:{trend_up} | Down:{trend_down} | MomUp:{mom_up} | MomDown:{mom_down} | Vol:{vol_ok}")

        # 🎯 PROFESYONEL SCORE
        score = 0
        if trend_up or trend_down: score += 20
        if mom_up or mom_down: score += 20
        if vol_ok: score += 20
        if 42 < rsi_val < 58: score += 20

        if score < 60:
            return None

        # 🔥 EN KALİTELİ FİLTRE (HEPSİ ŞART)
        if trend_up and mom_up and vol_ok and 52 < rsi_val < 58:
            direction = "LONG"
        elif trend_down and mom_down and vol_ok and 42 < rsi_val < 48:
            direction = "SHORT"
        else:
            return None

        return {
            "symbol": symbol,
            "price": price,
            "score": score,
            "direction": direction,
            "rsi": rsi_val
        }

    except Exception as e:
        print("Analyze error:", e)
        return None

# ---------------- MAIN LOOP ----------------
def run():
    global last_signal, last_time

    print("V83 PRO STARTED")

    while True:
        try:
            best = None

            for s in symbols:
                result = analyze(s)
                if result:
                    if not best or result["score"] > best["score"]:
                        best = result
                time.sleep(0.5)

            if best:
                key = f'{best["symbol"]}_{best["direction"]}'
                now = time.time()

                if key != last_signal and (now - last_time > COOLDOWN):
                    last_signal = key
                    last_time = now

                    price = best["price"]

                    if best["direction"] == "LONG":
                        tp = price * 1.01
                        sl = price * 0.995
                    else:
                        tp = price * 0.99
                        sl = price * 1.005

                    msg = f"""🚀 V83 PRO SIGNAL

Symbol: {best["symbol"]}
Direction: {best["direction"]}

Entry: {round(price,2)}
TP: {round(tp,2)}
SL: {round(sl,2)}

Score: {best["score"]}
RSI: {round(best["rsi"],2)}
"""

                    print("SIGNAL:", best)
                    send(msg)

            time.sleep(3)

        except Exception as e:
            print("Loop error:", e)
            time.sleep(5)

# ---------------- START ----------------
if __name__ == "__main__":
    send("🚀 V83 PRO ENGINE AKTİF")
    run()
