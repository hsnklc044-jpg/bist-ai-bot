import requests, time, pandas as pd

TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

symbols = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

last_signal = {}
cooldown = 300  # saniye

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print("Telegram hata:", e)

def get_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=100"
    data = requests.get(url, timeout=10).json()
    df = pd.DataFrame(data)
    df = df.iloc[:,:6]
    df.columns = ["time","open","high","low","close","volume"]
    df = df.astype(float)
    return df

def rsi(df, period=14):
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def signal(symbol):
    global last_signal

    df = get_data(symbol)
    df["rsi"] = rsi(df)

    last = df.iloc[-1]
    prev = df.iloc[-2]

    price = last["close"]

    # 🎯 TREND
    ema = df["close"].ewm(span=20).mean().iloc[-1]
    trend_up = price > ema

    # ⚡ MOMENTUM
    mom = last["rsi"] > 55

    # 📊 VOLUME
    vol = last["volume"] > df["volume"].rolling(20).mean().iloc[-1]

    # 🧠 SCORE
    score = 0
    if trend_up: score += 20
    if mom: score += 20
    if vol: score += 20

    print(f"{symbol} Score:{score} Trend:{trend_up} Mom:{mom} Vol:{vol}")

    # 🚫 COOLDOWN
    now = time.time()
    if symbol in last_signal and now - last_signal[symbol] < cooldown:
        return

    # 🚀 ENTRY LOGIC
    if score >= 20:
        direction = "LONG" if trend_up else "SHORT"

        msg = f"""🚀 V72 SMART ENTRY {symbol}
Dir: {direction}
Price: {round(price,2)}
Score: {score}
RSI: {round(last["rsi"],2)}"""

        send(msg)
        last_signal[symbol] = now

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
    send("🚀 V72 SMART ENGINE AKTİF")
    run()
