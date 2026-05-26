import requests
import pandas as pd
import time

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

symbols = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

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

def rsi(df, p=14):
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    rs = gain.rolling(p).mean() / loss.rolling(p).mean()
    return 100 - (100/(1+rs))

def atr(df):
    return (df["high"] - df["low"]).rolling(14).mean()

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

def signal(symbol):
    df5 = get_data(symbol,"5m")
    df15 = get_data(symbol,"15m")

    atr_val = atr(df5).iloc[-1]
    sw = sweep(df5)
    tr = trend(df15)
    vol = volume(df5)
    mom = momentum(df5)

    score = 0
    if sw: score += 40
    if tr: score += 20
    if vol: score += 20
    if mom: score += 20

    print(symbol,"Score:",score,"Sweep:",sw,"Trend:",tr,"Vol:",vol,"Mom:",mom)

    # 🔥 HYBRID ENTRY
    if (sw and score >= 40) or (mom and vol and score >= 40):
        price = df5["close"].iloc[-1]
        send_telegram(f"🚀 V70.1 ENTRY {symbol} {price} | Score:{score}")

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
