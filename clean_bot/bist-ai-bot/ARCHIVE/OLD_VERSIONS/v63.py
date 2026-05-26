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
def open_trade(symbol, price, s, r, atr_val):
    tp = price + atr_val * 2
    sl = price - atr_val * 1.2

    OPEN_TRADES[symbol] = {
        "entry": price,
        "tp": tp,
        "sl": sl
    }

    LAST_SIGNAL[symbol] = time.time()

    send_telegram(
        f"🚀 ENTRY {symbol}\n"
        f"Price: {price}\n"
        f"Score: {s}\n"
        f"RSI: {round(r,2)}\n"
        f"ATR: {round(atr_val,4)}\n"
        f"TP: {round(tp,4)}\n"
        f"SL: {round(sl,4)}"
    )

def manage_trade(symbol, price):
    if symbol not in OPEN_TRADES:
        return

    t = OPEN_TRADES[symbol]

    if price >= t["tp"]:
        send_telegram(f"✅ TP {symbol}")
        del OPEN_TRADES[symbol]

    elif price <= t["sl"]:
        send_telegram(f"❌ SL {symbol}")
        del OPEN_TRADES[symbol]

# ================= RUN =================
def run():
    send_telegram("🚀 V63 VOLATILITY ENGINE AKTİF")

    while True:
        try:
            for symbol in COINS:

                df = get_data(symbol)
                price = df["c"].iloc[-1]

                manage_trade(symbol, price)

                s, r = score(df)
                atr_val = atr(df)

                print(symbol, "Score:", s, "RSI:", round(r,2), "ATR:", round(atr_val,4))

                if s >= 60 and can_trade(symbol):
                    open_trade(symbol, price, s, r, atr_val)

                time.sleep(0.5)

            time.sleep(20)

        except Exception as e:
            print("HATA:", e)
            time.sleep(5)

if __name__ == "__main__":
    run()
