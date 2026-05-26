import time
import requests
import pandas as pd

BOT_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

session = requests.Session()

def send_telegram(msg):
    try:
        session.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=10
        )
    except:
        pass

def get_data(symbol):
    r = session.get(
        "https://api.binance.com/api/v3/klines",
        params={"symbol":symbol,"interval":"5m","limit":100},
        timeout=10
    ).json()

    df = pd.DataFrame(r, columns=["t","o","h","l","c","v","ct","qv","n","tb","tq","ig"])
    df["c"] = df["c"].astype(float)
    return df

def rsi(series):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    return 100 - (100/(1+rs))

def ema(series, span):
    return series.ewm(span=span).mean()

def trend(series):
    return ema(series,20) > ema(series,50)

def market_ok(series):
    e20 = ema(series,20)
    e50 = ema(series,50)
    return abs(e20.iloc[-1] - e50.iloc[-1]) / series.iloc[-1] > 0.001  # gevşettik

def signal(df, symbol):
    c = df["c"]
    r = rsi(c).iloc[-1]
    t = trend(c).iloc[-1]
    m = market_ok(c)

    print(symbol, "RSI:", round(r,2), "TREND:", t, "MARKET:", m)

    # 🔥 PROFESYONEL RANGE (genişletildi)
    return t and m and 40 < r < 75

def run():
    send_telegram("🚀 V61.1 DEBUG AKTİF")

    while True:
        try:
            for symbol in COINS:
                df = get_data(symbol)
                price = df["c"].iloc[-1]

                if signal(df, symbol):
                    send_telegram(f"🔥 SIGNAL {symbol} {price}")

                time.sleep(0.5)

            time.sleep(20)

        except Exception as e:
            print("HATA:", e)
            time.sleep(5)

if __name__ == "__main__":
    run()
