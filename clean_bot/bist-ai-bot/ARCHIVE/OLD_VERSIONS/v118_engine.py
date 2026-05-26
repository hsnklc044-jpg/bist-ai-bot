import requests
import pandas as pd
import time

API_KEY = "eTav5oGlcYvGO151lVlDRmv77zn9z8RzZThI27eQv7qKAaVzxwI1FZ1vXtZZEZLg"
BASE_URL = "https://api.binance.com/api/v3/klines"

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT", "BNBUSDT"]
INTERVAL = "5m"
LIMIT = 100

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"


def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data)
    except:
        pass


def get_data(symbol):
    params = {"symbol": symbol, "interval": INTERVAL, "limit": LIMIT}
    data = requests.get(BASE_URL, params=params).json()

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "ct","qv","n","tbb","tbq","ignore"
    ])

    df = df.astype(float)
    return df


def ema(df):
    df["ema"] = df["close"].ewm(span=50).mean()
    return df


def signal(df):
    df = ema(df)

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # TREND
    if last["close"] < last["ema"]:
        return None

    # BREAKOUT
    recent_high = df["high"].iloc[-20:].max()
    if last["close"] < recent_high:
        return None

    # RETEST (yumuşatıldı)
    if abs(prev["low"] - recent_high) / recent_high > 0.004:
        return None

    # CANDLE STRENGTH (yumuşatıldı)
    strength = (last["close"] - last["open"]) / (last["high"] - last["low"] + 1e-6)
    if strength < 0.45:
        return None

    # VOLUME (yumuşatıldı)
    avg_volume = df["volume"].rolling(20).mean().iloc[-1]
    if last["volume"] < avg_volume * 0.8:
        return None

    return "LONG"


def run():
    print("🚀 V118.1 FAST TEST ENGINE STARTED")
    send_telegram("🔥 V118.1 BAŞLADI")

    while True:
        for symbol in SYMBOLS:
            try:
                print("CHECK:", symbol)

                df = get_data(symbol)
                sig = signal(df)

                if sig == "LONG":
                    price = df.iloc[-1]["close"]

                    msg = f"🚨 TRADE\n{symbol}\nLONG\nEntry: {round(price,2)}"
                    print(msg)
                    send_telegram(msg)

            except Exception as e:
                print("ERROR:", symbol, e)

        time.sleep(60)


if __name__ == "__main__":
    run()