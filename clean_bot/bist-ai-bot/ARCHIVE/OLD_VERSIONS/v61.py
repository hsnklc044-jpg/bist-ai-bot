import time
import requests
import pandas as pd

BOT_TOKEN = "eTav5oGlcYvGO151lVlDRmv77zn9z8RzZThI27eQv7qKAaVzxwI1FZ1vXtZZEZLg"
CHAT_ID = "1790584407"

BALANCE = 1000
RISK_PER_TRADE = 0.02
MAX_OPEN_TRADES = 2
DAILY_LOSS_LIMIT = 0.05  # %5 zarar stop

COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

OPEN_TRADES = {}
LAST_TRADE_TIME = {}
DAILY_PNL = 0

session = requests.Session()

# ================= SAFE REQUEST =================
def safe_get(url, params, retries=5):
    delay = 1
    for i in range(retries):
        try:
            r = session.get(url, params=params, timeout=10)
            return r.json()
        except Exception as e:
            print("API HATA:", e)
            time.sleep(delay)
            delay *= 2
    return None

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
    data = safe_get(
        "https://api.binance.com/api/v3/klines",
        {"symbol":symbol,"interval":"5m","limit":100}
    )
    if data is None:
        return None

    df = pd.DataFrame(data, columns=["t","o","h","l","c","v","ct","qv","n","tb","tq","ig"])
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

def trend(series):
    return ema(series,20) > ema(series,50)

def market_ok(series):
    e20 = ema(series,20)
    e50 = ema(series,50)
    return abs(e20.iloc[-1] - e50.iloc[-1]) / series.iloc[-1] > 0.002

# ================= POSITION =================
def qty(price):
    return round((BALANCE * RISK_PER_TRADE) / (price * 0.03),3)

# ================= PROTECTION =================
def can_trade(symbol):
    if len(OPEN_TRADES) >= MAX_OPEN_TRADES:
        return False

    if DAILY_PNL < -BALANCE * DAILY_LOSS_LIMIT:
        print("DAILY STOP AKTİF")
        return False

    if symbol in LAST_TRADE_TIME:
        if time.time() - LAST_TRADE_TIME[symbol] < 300:
            return False

    return True

# ================= TRADE =================
def open_trade(symbol, price):
    global LAST_TRADE_TIME

    OPEN_TRADES[symbol] = {
        "entry":price,
        "tp":price*1.03,
        "sl":price*0.97,
        "qty":qty(price),
        "be":False
    }

    LAST_TRADE_TIME[symbol] = time.time()

    send_telegram(
        f"🚀 ENTRY {symbol}\n"
        f"Price: {price}\n"
        f"Qty: {OPEN_TRADES[symbol]['qty']}\n"
        f"TP: {round(price*1.03,4)}\n"
        f"SL: {round(price*0.97,4)}"
    )

def manage_trade(symbol, price):
    global DAILY_PNL

    if symbol not in OPEN_TRADES:
        return

    t = OPEN_TRADES[symbol]

    # BE
    if not t["be"] and price >= t["entry"]*1.01:
        t["sl"] = t["entry"]
        t["be"] = True

    # trailing
    if t["be"]:
        t["sl"] = max(t["sl"], price*0.985)

    # TP
    if price >= t["tp"]:
        pnl = (t["tp"] - t["entry"]) * t["qty"]
        DAILY_PNL += pnl
        send_telegram(f"✅ TP {symbol} PNL:{round(pnl,2)}")
        del OPEN_TRADES[symbol]

    # SL
    elif price <= t["sl"]:
        pnl = (t["sl"] - t["entry"]) * t["qty"]
        DAILY_PNL += pnl
        send_telegram(f"❌ SL {symbol} PNL:{round(pnl,2)}")
        del OPEN_TRADES[symbol]

# ================= SIGNAL =================
def signal(df):
    c = df["c"]
    r = rsi(c).iloc[-1]
    t = trend(c).iloc[-1]
    m = market_ok(c)

    return t and m and 45 < r < 70

# ================= RUN =================
def run():
    send_telegram("🚀 V61 PROTECT AKTİF")

    while True:
        try:
            for symbol in COINS:

                df = get_data(symbol)
                if df is None:
                    continue

                price = df["c"].iloc[-1]

                manage_trade(symbol, price)

                if not can_trade(symbol):
                    continue

                if signal(df):
                    if symbol not in OPEN_TRADES:
                        open_trade(symbol, price)

                print(symbol, "OK")

                time.sleep(0.5)

            time.sleep(30)

        except Exception as e:
            print("GENEL HATA:", e)
            time.sleep(5)

if __name__ == "__main__":
    run()
