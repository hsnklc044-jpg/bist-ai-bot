import time
import requests
import pandas as pd

BOT_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

session = requests.Session()

OPEN_TRADE = None

# ================= TELEGRAM =================
def send_telegram(msg):
    try:
        session.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=10
        )
    except:
        pass

# ================= DATA =================
def get_data(symbol):
    r = session.get(
        "https://api.binance.com/api/v3/klines",
        params={"symbol":symbol,"interval":"5m","limit":100},
        timeout=10
    ).json()

    df = pd.DataFrame(r, columns=["t","o","h","l","c","v","ct","qv","n","tb","tq","ig"])
    df[["h","l","c"]] = df[["h","l","c"]].astype(float)
    return df

# ================= INDICATORS =================
def rsi(series):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    return 100 - (100/(1+rs))

def ema(series, span):
    return series.ewm(span=span).mean()

# ================= SCORE =================
def score(df):
    c = df["c"]

    r = rsi(c).iloc[-1]
    e20 = ema(c,20).iloc[-1]
    e50 = ema(c,50).iloc[-1]

    momentum = c.iloc[-1] - c.iloc[-3]

    s = 0

    if e20 > e50:
        s += 40

    if 30 < r < 70:
        s += 40

    if momentum > 0:
        s += 20

    return s, r, momentum

# ================= SMART PICK =================
def get_best():
    best = None

    for symbol in COINS:
        df = get_data(symbol)
        s, r, m = score(df)
        price = df["c"].iloc[-1]

        print(symbol, "Score:", s, "RSI:", round(r,2))

        if s >= 40:

            # 🎯 RSI 50'ye ne kadar yakın?
            rsi_quality = abs(50 - r)

            candidate = {
                "symbol": symbol,
                "score": s,
                "rsi": r,
                "price": price,
                "quality": rsi_quality,
                "momentum": m
            }

            if best is None:
                best = candidate
            else:
                # 🔥 seçim mantığı
                if candidate["score"] > best["score"]:
                    best = candidate
                elif candidate["score"] == best["score"]:
                    if candidate["quality"] < best["quality"]:
                        best = candidate
                    elif candidate["momentum"] > best["momentum"]:
                        best = candidate

    return best

# ================= TRADE =================
def open_trade(data):
    global OPEN_TRADE

    OPEN_TRADE = data

    send_telegram(
        f"🚀 ELITE ENTRY {data['symbol']}\n"
        f"Price: {data['price']}\n"
        f"Score: {data['score']}\n"
        f"RSI: {round(data['rsi'],2)}"
    )

# ================= RUN =================
def run():
    send_telegram("🚀 V65.1 SMART AKTİF")

    while True:
        try:
            global OPEN_TRADE

            if OPEN_TRADE is None:
                best = get_best()

                if best:
                    open_trade(best)

            time.sleep(20)

        except Exception as e:
            print("HATA:", e)
            time.sleep(5)

if __name__ == "__main__":
    run()
