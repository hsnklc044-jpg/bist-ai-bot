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
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        session.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        pass

def get_data(symbol, interval):
    url = "https://api.binance.com/api/v3/klines"
    data = session.get(url, params={"symbol":symbol,"interval":interval,"limit":100}, timeout=10).json()

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
    risk_amount = BALANCE * RISK_PER_TRADE
    qty = risk_amount / (price * 0.03)
    return round(qty,3)

# ================= TRADE =================
def open_trade(symbol, price):
    sl = price * 0.97
    tp = price * 1.03
    qty = calculate_position(price)

    OPEN_TRADES[symbol] = {"entry":price,"tp":tp,"sl":sl,"qty":qty,"be":False}

    send_telegram(f"🚀 ENTRY {symbol}\nPrice:{price}\nQty:{qty}")

def manage_trade(symbol, price):
    if symbol not in OPEN_TRADES:
        return

    t = OPEN_TRADES[symbol]

    if not t["be"] and price >= t["entry"] * 1.01:
        t["sl"] = t["entry"]
        t["be"] = True

    if t["be"]:
        new_sl = price * 0.985
        if new_sl > t["sl"]:
            t["sl"] = new_sl

    if price >= t["tp"]:
        send_telegram(f"✅ TP {symbol}")
        del OPEN_TRADES[symbol]
    elif price <= t["sl"]:
        send_telegram(f"❌ EXIT {symbol}")
        del OPEN_TRADES[symbol]

# ================= PULLBACK =================
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
    ema20 = ema(close,20)
    price = close.iloc[-1]

    # fiyat EMA20'ye yakınsa
    return abs(price - ema20.iloc[-1]) / price < 0.003

# ================= RUN =================
def run():
    send_telegram("🚀 V58 DUAL PULLBACK AKTİF")

    while True:
        try:
            for symbol in COINS:

                df5 = get_data(symbol,"5m")
                df15 = get_data(symbol,"15m")
                df1h = get_data(symbol,"1h")

                c5 = df5["c"]
                c15 = df15["c"]
                c1h = df1h["c"]

                price = c5.iloc[-1]
                r = rsi(c5).iloc[-1]

                t5 = trend(c5).iloc[-1]
                t15 = trend(c15).iloc[-1]
                t1h = trend(c1h).iloc[-1]

                print(symbol,"RSI:",round(r,2),"T5:",t5,"T15:",t15,"T1H:",t1h)

                manage_trade(symbol, price)

                if len(OPEN_TRADES) >= MAX_OPEN_TRADES:
                    continue

                if t5 and t15 and t1h:

                    if rsi_pullback(symbol, r) or price_pullback(c5):
                        if symbol not in OPEN_TRADES:
                            open_trade(symbol, price)

            time.sleep(60)

        except Exception as e:
            print("HATA:", e)
            time.sleep(5)

if __name__ == "__main__":
    run()
