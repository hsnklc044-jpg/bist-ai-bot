import requests, time, pandas as pd

TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

symbols = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

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
    df = get_data(symbol)

    df["rsi"] = rsi(df)
    last = df.iloc[-1]

    score = 0
    vol = last["volume"] > df["volume"].rolling(20).mean().iloc[-1]
    mom = last["rsi"] > 50

    if vol: score += 10
    if mom: score += 10

    print(f"{symbol} Score:{score}")

    # ✅ TEST MODE (gevşek entry)
    if score >= 20:
        price = last["close"]

        msg = f"""🚀 V71.1 TEST ENTRY {symbol}
Price: {price}
Score: {score}
RSI: {round(last["rsi"],2)}"""

        send(msg)

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
    send("🚀 V71.1 TEST MODE AKTİF")
    run()
