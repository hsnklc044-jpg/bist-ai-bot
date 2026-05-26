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
    except:
        pass

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

# ---------------- ATR ----------------
def atr(data, period=14):
    trs = []
    for i in range(1, len(data)):
        high = float(data[i][2])
        low = float(data[i][3])
        prev_close = float(data[i-1][4])
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)
    return sum(trs[-period:]) / period

# ---------------- BTC TREND ----------------
def btc_trend():
    data = get_data("BTCUSDT", "15m")
    if not data:
        return None

    closes = [float(x[4]) for x in data]
    ema20 = ema(closes, 20)

    if closes[-1] > ema20[-1]:
        return "UP"
    elif closes[-1] < ema20[-1]:
        return "DOWN"
    return "SIDE"

# ---------------- ANALYZE ----------------
def analyze(symbol, btc_direction):
    data5 = get_data(symbol, "5m")
    data15 = get_data(symbol, "15m")

    if not data5 or not data15:
        return None

    closes = [float(x[4]) for x in data5]
    volumes = [float(x[5]) for x in data5]

    price = closes[-1]

    ema20 = ema(closes, 20)
    ema15 = ema([float(x[4]) for x in data15], 20)

    rsi_val = rsi(closes)
    atr_val = atr(data5)

    vol_avg = sum(volumes[-15:]) / 15
    vol_ratio = volumes[-1] / vol_avg

    vol_ok = vol_ratio > 1.0
    vol_strong = vol_ratio > 1.2

    trend_up = price > ema20[-1]
    trend_down = price < ema20[-1]

    mtf_up = float(data15[-1][4]) > ema15[-1]
    mtf_down = float(data15[-1][4]) < ema15[-1]

    mom_up = closes[-1] > closes[-3]
    mom_down = closes[-1] < closes[-3]

    # DEBUG
    print(f"{symbol} | RSI:{round(rsi_val,2)} | VOL_RATIO:{round(vol_ratio,2)} | MOM_UP:{mom_up} | MOM_DOWN:{mom_down} | TREND_UP:{trend_up} | TREND_DOWN:{trend_down}")

    # SCORE SYSTEM
    score = 0
    if trend_up or trend_down: score += 25
    if mtf_up or mtf_down: score += 25
    if mom_up or mom_down: score += 20
    if vol_strong: score += 30

    if score < 60:
        return None

    # SIGNAL LOGIC
    if btc_direction == "UP":
        if not (trend_up and mtf_up and mom_up and 48 < rsi_val < 68):
            return None
        direction = "LONG"

    elif btc_direction == "DOWN":
        if not (trend_down and mtf_down and mom_down and 32 < rsi_val < 55):
            return None
        direction = "SHORT"

    else:
        return None

    return {
        "symbol": symbol,
        "price": price,
        "direction": direction,
        "rsi": rsi_val,
        "atr": atr_val,
        "btc": btc_direction,
        "score": score
    }

# ---------------- MAIN ----------------
def run():
    global last_signal, last_time

    print("V88 PRO STARTED")

    while True:
        try:
            btc_direction = btc_trend()
            print("BTC TREND:", btc_direction)

            if btc_direction == "SIDE":
                time.sleep(6)
                continue

            for s in symbols:
                result = analyze(s, btc_direction)

                if result:
                    key = f'{result["symbol"]}_{result["direction"]}'
                    now = time.time()

                    if key != last_signal and (now - last_time > COOLDOWN):
                        last_signal = key
                        last_time = now

                        price = result["price"]
                        atr_val = result["atr"]

                        if result["direction"] == "LONG":
                            tp = price + (atr_val * 1.3)
                            sl = price - atr_val
                        else:
                            tp = price - (atr_val * 1.3)
                            sl = price + atr_val

                        msg = f"""🚀 V88 PRO

Symbol: {result["symbol"]}
Direction: {result["direction"]}

Entry: {round(price,2)}
TP: {round(tp,2)}
SL: {round(sl,2)}

Score: {result["score"]}
RSI: {round(result["rsi"],2)}
BTC: {result["btc"]}
"""
                        print("SIGNAL:", result)
                        send(msg)

                time.sleep(0.3)

            time.sleep(4)

        except Exception as e:
            print("Loop error:", e)
            time.sleep(5)

# ---------------- START ----------------
if __name__ == "__main__":
    send("🚀 V88 PRO AKTİF")
    run()