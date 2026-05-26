import requests
import pandas as pd
import time

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

symbols = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

state = {}
last_signal_time = {}
last_direction = {}

COOLDOWN = 180

def send_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def get_data(symbol, interval="5m", limit=100):
    data = requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}").json()
    df = pd.DataFrame(data).iloc[:, :6]
    df.columns = ["time","open","high","low","close","volume"]

    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df

def sweep(df):
    l = df.iloc[-1]
    p = df.iloc[-2]

    if l["high"] > p["high"] and l["close"] < p["high"]:
        return "SHORT"
    if l["low"] < p["low"] and l["close"] > p["low"]:
        return "LONG"
    return None

def trend(df):
    return df["close"].iloc[-1] > df["close"].rolling(20).mean().iloc[-1]

def volume(df):
    return df["volume"].iloc[-1] > df["volume"].rolling(20).mean().iloc[-1]

def momentum(df):
    return df["close"].iloc[-1] > df["close"].iloc[-3]

def cooldown_ok(symbol):
    now = time.time()
    if symbol not in last_signal_time:
        return True
    return (now - last_signal_time[symbol]) > COOLDOWN

def signal(symbol):
    df5 = get_data(symbol,"5m")
    df15 = get_data(symbol,"15m")

    sw = sweep(df5)
    tr = trend(df15)
    vol = volume(df5)
    mom = momentum(df5)

    score = 0
    if sw: score += 40
    if tr: score += 20
    if vol: score += 20
    if mom: score += 20

    price = df5["close"].iloc[-1]
    current_state = state.get(symbol, "NONE")

    print(symbol,"Score:",score,"State:",current_state,"Dir:",last_direction.get(symbol))

    # 🔒 ENTRY LOCK
    if sw:
        if current_state != "ENTRY" and cooldown_ok(symbol):
            send_telegram(f"🚀 ENTRY {symbol} {price} | Dir:{sw} | Score:{score}")
            state[symbol] = "ENTRY"
            last_direction[symbol] = sw
            last_signal_time[symbol] = time.time()
            return

    # ⚡ WATCH
    if score >= 20 and current_state == "NONE":
        if cooldown_ok(symbol):
            send_telegram(f"⚡ WATCH {symbol} {price} | Score:{score}")
            state[symbol] = "WATCH"
            last_signal_time[symbol] = time.time()
            return

    # 🔄 RESET (kritik)
    if current_state == "ENTRY":
        # trend tersine dönerse reset
        if (last_direction[symbol] == "LONG" and not tr) or \
           (last_direction[symbol] == "SHORT" and tr):
            print("RESET:", symbol)
            state[symbol] = "NONE"
            last_direction[symbol] = None

    elif score < 20:
        state[symbol] = "NONE"

def run():
    while True:
        try:
            for s in symbols:
                signal(s)
                time.sleep(1)
            time.sleep(20)
        except Exception as e:
            print("HATA:", e)
            time.sleep(5)

if __name__ == "__main__":
    run()
