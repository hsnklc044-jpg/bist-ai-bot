import time
import requests
import pandas as pd

BOT_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

session = requests.Session()

OPEN_TRADES = {}
LAST_SIGNAL = {}

MAX_TRADES = 2
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
    df["c"] = df["c"].astype(float)
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

    s = 0

    if e20 > e50:
        s += 40

    if 40 < r < 60:
        s += 40
    elif 60 <= r < 70:
        s += 20

    if c.iloc[-1] > c.iloc[-3]:
        s += 20

    return s, r

# ================= FILTER =================
def can_trade(symbol):
    if symbol in OPEN_TRADES:
        return False

    if len(OPEN_TRADES) >= MAX_TRADES:
        return False

    if symbol in LAST_SIGNAL:
        if time.time() - LAST_SIGNAL[symbol] < COOLDOWN:
            return False

    return True

# ================= TRADE =================
def open_trade(symbol, price, s, r):
    OPEN_TRADES[symbol] = {
        "entry": price,
        "tp": price * 1.02,
        "sl": price * 0.98,
        "be": False
    }

    LAST_SIGNAL[symbol] = time.time()

    send_telegram(
        f"🚀 ENTRY {symbol}\n"
        f"Price: {price}\n"
        f"Score: {s}\n"
        f"RSI: {round(r,2)}\n"
        f"TP: {round(price*1.02,4)}\n"
        f"SL: {round(price*0.98,4)}"
    )

def manage_trade(symbol, price):
    if symbol not in OPEN_TRADES:
        return

    t = OPEN_TRADES[symbol]

    # break-even
    if not t["be"] and price >= t["entry"] * 1.01:
        t["sl"] = t["entry"]
        t["be"] = True

    # TP
    if price >= t["tp"]:
        send_telegram(f"✅ TP {symbol}")
        del OPEN_TRADES[symbol]

    # SL
    elif price <= t["sl"]:
        send_telegram(f"❌ SL {symbol}")
        del OPEN_TRADES[symbol]

# ================= RUN =================
def run():
    send_telegram("🚀 V62.2 FULL ENGINE AKTİF")

    while True:
        try:
            for symbol in COINS:

                df = get_data(symbol)
                price = df["c"].iloc[-1]

                manage_trade(symbol, price)

                s, r = score(df)

                print(symbol, "Score:", s, "RSI:", round(r,2))

                if s >= 60 and can_trade(symbol):
                    open_trade(symbol, price, s, r)

                time.sleep(0.5)

            time.sleep(20)

        except Exception as e:
            print("HATA:", e)
            time.sleep(5)

if __name__ == "__main__":
    run()
