import time
import requests
import json

symbols = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

last_signal = None
last_time = 0
COOLDOWN = 240

trades = []

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

    if closes[-1] > ema20[-1] and ema20[-1] > ema20[-3]:
        return "UP"
    elif closes[-1] < ema20[-1] and ema20[-1] < ema20[-3]:
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
    vol_ok = volumes[-1] > vol_avg * 1.1

    trend_up = price > ema20[-1] and ema20[-1] > ema20[-3]
    trend_down = price < ema20[-1] and ema20[-1] < ema20[-3]

    mtf_up = float(data15[-1][4]) > ema15[-1]
    mtf_down = float(data15[-1][4]) < ema15[-1]

    pullback_long = closes[-2] < ema20[-1] and closes[-1] > ema20[-1]
    pullback_short = closes[-2] > ema20[-1] and closes[-1] < ema20[-1]

    if btc_direction == "UP":
        if not (trend_up and mtf_up and pullback_long and 50 < rsi_val < 65 and vol_ok):
            return None
        direction = "LONG"

    elif btc_direction == "DOWN":
        if not (trend_down and mtf_down and pullback_short and 35 < rsi_val < 50 and vol_ok):
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
        "btc": btc_direction
    }

# ---------------- TRADE TRACK ----------------
def track_trades():
    global trades

    for t in trades:
        if t["status"] != "OPEN":
            continue

        data = get_data(t["symbol"])
        if not data:
            continue

        price = float(data[-1][4])

        if t["direction"] == "LONG":
            if price >= t["tp"]:
                t["status"] = "WIN"
                send(f"✅ WIN {t['symbol']}")
            elif price <= t["sl"]:
                t["status"] = "LOSS"
                send(f"❌ LOSS {t['symbol']}")

        else:
            if price <= t["tp"]:
                t["status"] = "WIN"
                send(f"✅ WIN {t['symbol']}")
            elif price >= t["sl"]:
                t["status"] = "LOSS"
                send(f"❌ LOSS {t['symbol']}")

# ---------------- STATS ----------------
def stats():
    wins = sum(1 for t in trades if t["status"] == "WIN")
    losses = sum(1 for t in trades if t["status"] == "LOSS")

    total = wins + losses
    if total == 0:
        return "No trades yet"

    winrate = (wins / total) * 100
    return f"Trades: {total} | Win: {wins} | Loss: {losses} | WR: {round(winrate,2)}%"

# ---------------- MAIN ----------------
def run():
    global last_signal, last_time, trades

    print("V86 ELITE+ TRACKING STARTED")

    while True:
        try:
            btc_direction = btc_trend()

            if btc_direction == "SIDE":
                time.sleep(10)
                continue

            track_trades()

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
                            tp = price + (atr_val * 1.5)
                            sl = price - atr_val
                        else:
                            tp = price - (atr_val * 1.5)
                            sl = price + atr_val

                        trades.append({
                            "symbol": result["symbol"],
                            "direction": result["direction"],
                            "tp": tp,
                            "sl": sl,
                            "status": "OPEN"
                        })

                        msg = f"""🚀 V86 ELITE+

Symbol: {result["symbol"]}
Direction: {result["direction"]}

Entry: {round(price,2)}
TP: {round(tp,2)}
SL: {round(sl,2)}

RSI: {round(result["rsi"],2)}
BTC: {result["btc"]}

{stats()}
"""
                        send(msg)

                time.sleep(0.5)

            time.sleep(5)

        except Exception as e:
            print("Loop error:", e)
            time.sleep(5)

# ---------------- START ----------------
if __name__ == "__main__":
    send("🚀 V86 ELITE+ TRACKING AKTİF")
    run()