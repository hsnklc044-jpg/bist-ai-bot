import time
import requests
import pandas as pd

BOT_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

session = requests.Session()

OPEN_TRADE = None
LAST_SIGNAL = {}

COOLDOWN = 300

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

def atr(df):
    high = df["h"]
    low = df["l"]
    close = df["c"]

    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)

    return tr.rolling(14).mean().iloc[-1]

# ================= SCORE =================
def score(df):
    c = df["c"]

    r = rsi(c).iloc[-1]
    e20 = ema(c,20).iloc[-1]
    e50 = ema(c,50).iloc[-1]

    s = 0

    if e20 > e50:
        s += 40

    if 30 < r < 70:
        s += 40
    elif 70 <= r < 80:
        s += 20

    if c.iloc[-1] > c.iloc[-3]:
        s += 20

    return s, r

# ================= BEST COIN =================
def get_best():
    best = None

    for symbol in COINS:
        df = get_data(symbol)
        s, r = score(df)
        price = df["c"].iloc[-1]
        atr_val = atr(df)

        print(symbol, "Score:", s, "RSI:", round(r,2))

        if s >= 40:
            if best is None or s > best["score"]:
                best = {
                    "symbol": symbol,
                    "score": s,
                    "rsi": r,
                    "price": price,
                    "atr": atr_val
                }

    return best

# ================= TRADE =================
def open_trade(data):
    global OPEN_TRADE

    price = data["price"]
    atr_val = data["atr"]

    tp = price + atr_val * 2
    sl = price - atr_val * 1.2

    OPEN_TRADE = {
        "symbol": data["symbol"],
        "entry": price,
        "tp": tp,
        "sl": sl,
        "half": False
    }

    send_telegram(
        f"🚀 BEST ENTRY {data['symbol']}\n"
        f"Price: {price}\n"
        f"Score: {data['score']}\n"
        f"RSI: {round(data['rsi'],2)}\n"
        f"TP: {round(tp,4)}\n"
        f"SL: {round(sl,4)}"
    )

def manage_trade():
    global OPEN_TRADE

    if not OPEN_TRADE:
        return

    df = get_data(OPEN_TRADE["symbol"])
    price = df["c"].iloc[-1]

    t = OPEN_TRADE

    if not t["half"] and price >= t["entry"] * 1.01:
        t["half"] = True
        t["sl"] = t["entry"]
        send_telegram(f"💰 HALF TP {t['symbol']}")

    if t["half"]:
        new_sl = price * 0.99
        if new_sl > t["sl"]:
            t["sl"] = new_sl

    if price >= t["tp"]:
        send_telegram(f"✅ TP {t['symbol']}")
        OPEN_TRADE = None

    elif price <= t["sl"]:
        send_telegram(f"❌ SL {t['symbol']}")
        OPEN_TRADE = None

# ================= RUN =================
def run():
    send_telegram("🚀 V65 ELITE ENGINE AKTİF")

    while True:
        try:
            manage_trade()

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
