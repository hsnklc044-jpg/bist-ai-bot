import time
import requests
import pandas as pd

BOT_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

MAX_OPEN_TRADES = 2

COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

OPEN_TRADES = {}

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        pass

def get_data(symbol):
    url = "https://api.binance.com/api/v3/klines"
    data = requests.get(url, params={"symbol":symbol,"interval":"5m","limit":100}).json()

    df = pd.DataFrame(data, columns=["t","o","h","l","c","v","ct","qv","n","tb","tq","ig"])
    df["c"] = df["c"].astype(float)
    return df

def rsi(series):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    return 100 - (100/(1+rs))

def trend(series):
    ema20 = series.ewm(span=20).mean()
    ema50 = series.ewm(span=50).mean()
    return ema20 > ema50

def open_trade(symbol, price):
    OPEN_TRADES[symbol] = {
        "entry": price,
        "tp": price * 1.03,
        "sl": price * 0.97
    }

    send_telegram(f"🚀 ENTRY {symbol}\nPrice: {round(price,4)}")

def check_trade(symbol, price):
    if symbol not in OPEN_TRADES:
        return

    t = OPEN_TRADES[symbol]

    if price >= t["tp"]:
        send_telegram(f"✅ TP {symbol}")
        del OPEN_TRADES[symbol]

    elif price <= t["sl"]:
        send_telegram(f"❌ SL {symbol}")
        del OPEN_TRADES[symbol]

def should_enter(score, trend_ok, r):
    return (
        score >= 50 and
        trend_ok and
        40 < r < 60   # 🔥 KRİTİK FİLTRE
    )

def run():
    send_telegram("🚀 V52.1 SMART ENTRY AKTİF")

    while True:
        try:
            for symbol in COINS:

                df = get_data(symbol)
                close = df["c"]

                price = close.iloc[-1]
                r = rsi(close).iloc[-1]
                tr = trend(close).iloc[-1]

                score = 0
                if close.iloc[-1] > close.iloc[-5]:
                    score += 50
                if 40 < r < 75:
                    score += 50

                print(symbol, "Score:",score,"RSI:",round(r,2),"Trend:",tr)

                check_trade(symbol, price)

                if len(OPEN_TRADES) >= MAX_OPEN_TRADES:
                    continue

                if should_enter(score, tr, r):
                    if symbol not in OPEN_TRADES:
                        open_trade(symbol, price)

            time.sleep(60)

        except Exception as e:
            print("HATA:", e)
            time.sleep(10)

if __name__ == "__main__":
    run()
