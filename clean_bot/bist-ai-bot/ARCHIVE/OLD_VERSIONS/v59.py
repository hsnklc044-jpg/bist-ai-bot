import time
import requests
import pandas as pd

BOT_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

BALANCE = 1000
RISK_PER_TRADE = 0.02
MAX_OPEN_TRADES = 2

COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

OPEN_TRADES = {}
PULLBACK_STATE = {}

session = requests.Session()

def send_telegram(msg):
    try:
        session.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                     data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        pass

def get_data(symbol, interval):
    data = session.get("https://api.binance.com/api/v3/klines",
                       params={"symbol":symbol,"interval":interval,"limit":100},
                       timeout=10).json()

    df = pd.DataFrame(data, columns=["t","o","h","l","c","v","ct","qv","n","tb","tq","ig"])
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

def calculate_position(price):
    return round((BALANCE * RISK_PER_TRADE) / (price * 0.03),3)

# ===== ENTRY =====
def open_trade(symbol, price):
    OPEN_TRADES[symbol] = {
        "entry":price,
        "tp":price*1.03,
        "sl":price*0.97,
        "qty":calculate_position(price),
        "be":False
    }

    send_telegram(f"🚀 ENTRY {symbol} {price}")

# ===== TRADE MGMT =====
def manage_trade(symbol, price):
    if symbol not in OPEN_TRADES:
        return

    t = OPEN_TRADES[symbol]

    if not t["be"] and price >= t["entry"]*1.01:
        t["sl"] = t["entry"]
        t["be"] = True

    if t["be"]:
        t["sl"] = max(t["sl"], price*0.985)

    if price >= t["tp"]:
        send_telegram(f"✅ TP {symbol}")
        del OPEN_TRADES[symbol]

    elif price <= t["sl"]:
        send_telegram(f"❌ EXIT {symbol}")
        del OPEN_TRADES[symbol]

# ===== PULLBACK =====
def rsi_pullback(symbol, r):
    if symbol not in PULLBACK_STATE:
        PULLBACK_STATE[symbol] = {"ob":False}

    s = PULLBACK_STATE[symbol]

    if r > 70:
        s["ob"] = True

    if s["ob"] and 45 < r < 60:
        s["ob"] = False
        return True

    return False

def price_pullback(close):
    e20 = ema(close,20).iloc[-1]
    price = close.iloc[-1]
    return abs(price-e20)/price < 0.003

# ===== BREAKOUT =====
def breakout(close):
    last_high = close.iloc[-20:-1].max()
    return close.iloc[-1] > last_high

# ===== RUN =====
def run():
    send_telegram("🚀 V59 ULTRA AKTİF")

    while True:
        try:
            for symbol in COINS:

                df = get_data(symbol,"5m")
                c = df["c"]

                price = c.iloc[-1]
                r = rsi(c).iloc[-1]

                t = trend(c).iloc[-1]

                print(symbol,"RSI:",round(r,2),"Trend:",t)

                manage_trade(symbol, price)

                if len(OPEN_TRADES) >= MAX_OPEN_TRADES:
                    continue

                if t:

                    if (
                        rsi_pullback(symbol,r) or
                        price_pullback(c) or
                        breakout(c)
                    ):
                        if symbol not in OPEN_TRADES:
                            open_trade(symbol, price)

            time.sleep(60)

        except Exception as e:
            print("HATA:", e)
            time.sleep(5)

if __name__ == "__main__":
    run()
