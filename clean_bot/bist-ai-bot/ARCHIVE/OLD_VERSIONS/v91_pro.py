import time
import requests

symbols = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

balance = 1000.0
risk_per_trade = 0.01

active_trade = None
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
def get_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        return float(requests.get(url, timeout=5).json()["price"])
    except:
        return None

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
    vol_ratio = volumes[-1] / vol_avg if vol_avg else 0

    trend_up = price > ema20[-1]
    trend_down = price < ema20[-1]

    mtf_up = float(data15[-1][4]) > ema15[-1]
    mtf_down = float(data15[-1][4]) < ema15[-1]

    mom_up = closes[-1] > closes[-3]
    mom_down = closes[-1] < closes[-3]

    score = 0
    if trend_up or trend_down: score += 25
    if mtf_up or mtf_down: score += 25
    if mom_up or mom_down: score += 20
    if vol_ratio > 1.2: score += 30

    if score < 60:
        return None

    # RSI'ı biraz trend tarafına çekiyoruz (kalite artışı)
    if btc_direction == "UP":
        if not (trend_up and mtf_up and mom_up and 50 < rsi_val < 70):
            return None
        direction = "LONG"

    elif btc_direction == "DOWN":
        if not (trend_down and mtf_down and mom_down and 30 < rsi_val < 50):
            return None
        direction = "SHORT"

    else:
        return None

    return {
        "symbol": symbol,
        "price": price,
        "direction": direction,
        "atr": atr_val,
        "score": score
    }

# ---------------- POSITION SIZE ----------------
def calc_position(balance, risk, entry, sl):
    risk_amount = balance * risk
    sl_distance = abs(entry - sl)
    if sl_distance == 0:
        return 0
    return risk_amount / sl_distance

# ---------------- MAIN ----------------
def run():
    global active_trade, balance, last_time

    print("V91 PRO STARTED")

    while True:
        try:
            # --- Açık trade takibi ---
            if active_trade:
                price = get_price(active_trade["symbol"])
                if price:
                    if active_trade["direction"] == "LONG":
                        if price >= active_trade["tp"]:
                            profit = balance * risk_per_trade * 2
                            balance += profit
                            send(f"✅ TP HIT | Balance: {round(balance,2)}")
                            active_trade = None
                        elif price <= active_trade["sl"]:
                            loss = balance * risk_per_trade
                            balance -= loss
                            send(f"❌ SL HIT | Balance: {round(balance,2)}")
                            active_trade = None
                    else:
                        if price <= active_trade["tp"]:
                            profit = balance * risk_per_trade * 2
                            balance += profit
                            send(f"✅ TP HIT | Balance: {round(balance,2)}")
                            active_trade = None
                        elif price >= active_trade["sl"]:
                            loss = balance * risk_per_trade
                            balance -= loss
                            send(f"❌ SL HIT | Balance: {round(balance,2)}")
                            active_trade = None

                time.sleep(3)
                continue

            # --- Yeni trade arama ---
            btc_direction = btc_trend()

            if btc_direction == "SIDE":
                time.sleep(6)
                continue

            best = None

            for s in symbols:
                result = analyze(s, btc_direction)
                if result:
                    if not best or result["score"] > best["score"]:
                        best = result
                time.sleep(0.2)

            if best and (time.time() - last_time > COOLDOWN):
                entry = best["price"]
                atr_val = best["atr"]

                # 🎯 RR 1:2
                if best["direction"] == "LONG":
                    sl = entry - atr_val
                    tp = entry + (atr_val * 2)
                else:
                    sl = entry + atr_val
                    tp = entry - (atr_val * 2)

                size = calc_position(balance, risk_per_trade, entry, sl)

                active_trade = {
                    "symbol": best["symbol"],
                    "direction": best["direction"],
                    "tp": tp,
                    "sl": sl
                }

                last_time = time.time()

                msg = f"""🚀 V91 PRO

Symbol: {best["symbol"]}
Direction: {best["direction"]}

Entry: {round(entry,2)}
TP: {round(tp,2)}
SL: {round(sl,2)}

RR: 1:2
Size: {round(size,4)}
Balance: {round(balance,2)}
"""
                send(msg)

            time.sleep(4)

        except Exception as e:
            print("Loop error:", e)
            time.sleep(5)

# ---------------- START ----------------
if __name__ == "__main__":
    send("🚀 V91 PRO AKTİF")
    run()