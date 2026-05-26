import requests
import pandas as pd
import time

BASE_URL = "https://api.binance.com/api/v3/klines"

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT", "BNBUSDT"]
INTERVAL = "5m"
LIMIT = 100

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"


def send_telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=5
        )
    except:
        pass


def get_data(symbol):
    try:
        params = {"symbol": symbol, "interval": INTERVAL, "limit": LIMIT}
        r = requests.get(BASE_URL, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()

        df = pd.DataFrame(data, columns=[
            "time","open","high","low","close","volume",
            "ct","qv","n","tbb","tbq","ignore"
        ])

        return df.astype(float)

    except Exception as e:
        print("DATA ERROR:", symbol, e)
        return None


def ema(df):
    df["ema"] = df["close"].ewm(span=50).mean()
    return df


def signal(df):
    df = ema(df)

    last = df.iloc[-1]

    # TREND
    if last["close"] < last["ema"]:
        return None

    # BREAKOUT (gevşetilmiş)
    recent_high = df["high"].iloc[-20:].max()
    if last["close"] < recent_high * 0.998:
        return None

    # ❌ RETEST KALDIRILDI

    # CANDLE STRENGTH
    strength = (last["close"] - last["open"]) / (last["high"] - last["low"] + 1e-6)
    if strength < 0.45:
        return None

    # VOLUME
    avg_volume = df["volume"].rolling(20).mean().iloc[-1]
    if last["volume"] < avg_volume * 0.8:
        return None

    return "LONG"


def run():
    print("🚀 V118.2 FAST SIGNAL ENGINE STARTED")
    send_telegram("🔥 V118.2 BAŞLADI")

    while True:
        for symbol in SYMBOLS:
            print("CHECK:", symbol)

            df = get_data(symbol)
            if df is None:
                continue

            sig = signal(df)

            if sig == "LONG":
                price = df.iloc[-1]["close"]

                msg = f"🚨 TRADE\n{symbol}\nLONG\nEntry: {round(price,2)}"
                print(msg)
                send_telegram(msg)

            time.sleep(1)

        time.sleep(30)


if __name__ == "__main__":
    run()