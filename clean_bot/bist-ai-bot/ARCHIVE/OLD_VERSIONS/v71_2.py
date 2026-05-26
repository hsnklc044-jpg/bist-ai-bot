import requests, time, pandas as pd

TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

symbols = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

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

def signal(symbol):
    df = get_data(symbol)
    last = df.iloc[-1]

    # 🔥 FULL TEST MODE (zorla sinyal)
    score = 20
    vol = True
    mom = True

    price = last["close"]

    print(f"{symbol} Score:{score}")

    msg = f"""🚀 V71.2 TEST ENTRY {symbol}
Price: {price}
Score: {score}
TEST MODE AKTİF"""

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
    send("🚀 V71.2 FULL TEST MODE AKTİF")
    run()
