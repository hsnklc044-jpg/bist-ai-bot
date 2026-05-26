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

# ================= AI SCORE =================
def score(df):
    c = df["c"]

    r = rsi(c).iloc[-1]
    e20 = ema(c,20).iloc[-1]
    e50 = ema(c,50).iloc[-1]

    s = 0

    # trend
    if e20 > e50:
        s += 40

    # RSI zone
    if 40 < r < 60:
        s += 40
    elif 60 <= r < 70:
        s += 20

    # momentum
    if c.iloc[-1] > c.iloc[-3]:
        s += 20

    return s, r, e20 > e50

def run():
    send_telegram("🚀 V62 AI ENTRY AKTİF")

    while True:
        try:
            for symbol in COINS:
                df = get_data(symbol)
                price = df["c"].iloc[-1]

                s, r, t = score(df)

                print(symbol, "Score:", s, "RSI:", round(r,2), "Trend:", t)

                # 🔥 ENTRY LOGIC
                if s >= 60:
                    send_telegram(
                        f"🚀 ENTRY {symbol}\n"
                        f"Price: {price}\n"
                        f"Score: {s}\n"
                        f"RSI: {round(r,2)}"
                    )

                time.sleep(0.5)

            time.sleep(20)

        except Exception as e:
            print("HATA:", e)
            time.sleep(5)

if __name__ == "__main__":
    run()
