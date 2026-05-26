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

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        pass

def get_data(symbol, interval):
    url = "https://api.binance.com/api/v3/klines"
    data = requests.get(url, params={"symbol":symbol,"interval":interval,"limit":100}).json()

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

# 🔥 LOT NORMALIZATION
def calculate_position(price):
    risk_amount = BALANCE * RISK_PER_TRADE
    sl_pct = 0.03

    raw_qty = risk_amount / (price * sl_pct)

    # görsel düzenleme (risk değişmez)
    if raw_qty < 1:
        qty = round(raw_qty, 4)
    elif raw_qty < 10:
        qty = round(raw_qty, 2)
    else:
        qty = round(raw_qty, 1)

    return qty

def open_trade(symbol, price):
    sl = price * 0.97
    tp = price * 1.03
    qty = calculate_position(price)

    OPEN_TRADES[symbol] = {
        "entry": price,
        "tp": tp,
        "sl": sl,
        "qty": qty
    }

    send_telegram(
        f"🚀 ENTRY {symbol}\n"
        f"Price: {round(price,4)}\n"
        f"Qty: {qty}\n"
        f"TP: {round(tp,4)}\n"
        f"SL: {round(sl,4)}"
    )

def check_trade(symbol, price):
    if symbol not in OPEN_TRADES:
        return

    t = OPEN_TRADES[symbol]

    if price >= t["tp"]:
        profit = (t["tp"] - t["entry"]) * t["qty"]
        send_telegram(f"✅ TP {symbol}\nProfit: {round(profit,2)}$")
        del OPEN_TRADES[symbol]

    elif price <= t["sl"]:
        loss = (t["entry"] - t["sl"]) * t["qty"]
        send_telegram(f"❌ SL {symbol}\nLoss: {round(loss,2)}$")
        del OPEN_TRADES[symbol]

def should_enter(score, t5, t15, t1h, r):
    return (
        score >= 50 and
        t5 and t15 and t1h and
        40 < r < 65
    )

def run():
    send_telegram("🚀 V54.2 CLEAN SYSTEM AKTİF")

    while True:
        try:
            for symbol in COINS:

                df5 = get_data(symbol, "5m")
                df15 = get_data(symbol, "15m")
                df1h = get_data(symbol, "1h")

                close5 = df5["c"]
                close15 = df15["c"]
                close1h = df1h["c"]

                price = close5.iloc[-1]
                r = rsi(close5).iloc[-1]

                t5 = trend(close5).iloc[-1]
                t15 = trend(close15).iloc[-1]
                t1h = trend(close1h).iloc[-1]

                score = 0
                if close5.iloc[-1] > close5.iloc[-5]:
                    score += 50
                if 40 < r < 75:
                    score += 50

                print(symbol, "Score:",score,"RSI:",round(r,2),"T5:",t5,"T15:",t15,"T1H:",t1h)

                check_trade(symbol, price)

                if len(OPEN_TRADES) >= MAX_OPEN_TRADES:
                    continue

                if should_enter(score, t5, t15, t1h, r):
                    if symbol not in OPEN_TRADES:
                        open_trade(symbol, price)

            time.sleep(60)

        except Exception as e:
            print("HATA:", e)
            time.sleep(10)

if __name__ == "__main__":
    run()
