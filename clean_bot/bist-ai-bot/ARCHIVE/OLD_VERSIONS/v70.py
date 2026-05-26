import requests
import pandas as pd
import time

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

symbols = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def get_data(symbol, interval="5m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url).json()

    df = pd.DataFrame(data)
    df = df.iloc[:, :6]
    df.columns = ["time","open","high","low","close","volume"]

    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df

def rsi(df, period=14):
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def atr(df, period=14):
    return (df["high"] - df["low"]).rolling(period).mean()

def liquidity_sweep(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    if last["high"] > prev["high"] and last["close"] < prev["high"]:
        return "SHORT"
    if last["low"] < prev["low"] and last["close"] > prev["low"]:
        return "LONG"

    return None

def trend(df):
    return df["close"].iloc[-1] > df["close"].rolling(20).mean().iloc[-1]

def volume_spike(df):
    return df["volume"].iloc[-1] > df["volume"].rolling(20).mean().iloc[-1]

def signal(symbol):
    df5 = get_data(symbol, "5m")
    df15 = get_data(symbol, "15m")

    df5["rsi"] = rsi(df5)
    df15["rsi"] = rsi(df15)

    atr_val = atr(df5).iloc[-1]

    sweep = liquidity_sweep(df5)
    trend_ok = trend(df15)
    vol_ok = volume_spike(df5)

    score = 0

    if sweep:
        score += 40
    if trend_ok:
        score += 30
    if vol_ok:
        score += 30

    print(symbol, "Score:", score, "Sweep:", sweep, "Trend:", trend_ok, "Vol:", vol_ok)

    # 🔥 AKTİF MOD (trade üretir)
    if score >= 40 and sweep and atr_val > 0:
        price = df5["close"].iloc[-1]
        send_telegram(f"🚀 V70 ENTRY {symbol} {price} | Score:{score} | {sweep}")

def run():
    while True:
        try:
            for symbol in symbols:
                signal(symbol)
                time.sleep(1)
            time.sleep(20)
        except Exception as e:
            print("HATA:", e)
            time.sleep(5)

if __name__ == "__main__":
    run()
