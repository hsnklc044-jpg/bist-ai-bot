import requests
import pandas as pd
import time

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

symbols = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

RISK_PERCENT = 2
BALANCE = 1000

state = {}
positions = {}

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def get_data(symbol, interval="5m", limit=100):
    data = requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}").json()
    df = pd.DataFrame(data).iloc[:, :6]
    df.columns = ["time","open","high","low","close","volume"]

    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df

def atr(df):
    return (df["high"] - df["low"]).rolling(14).mean()

def sweep(df):
    l = df.iloc[-1]
    p = df.iloc[-2]

    if l["high"] > p["high"] and l["close"] < p["high"]:
        return "SHORT"
    if l["low"] < p["low"] and l["close"] > p["low"]:
        return "LONG"
    return None

def trend(df):
    return df["close"].iloc[-1] > df["close"].rolling(20).mean().iloc[-1]

def volume(df):
    return df["volume"].iloc[-1] > df["volume"].rolling(20).mean().iloc[-1]

def momentum(df):
    return df["close"].iloc[-1] > df["close"].iloc[-3]

def position_size(entry, sl):
    risk_amount = BALANCE * (RISK_PERCENT / 100)
    risk_per_unit = abs(entry - sl)
    if risk_per_unit == 0:
        return 0
    return round(risk_amount / risk_per_unit, 4)

def open_trade(symbol, direction, price, atr_val):
    sl = price - atr_val * 1.5 if direction == "LONG" else price + atr_val * 1.5
    tp = price + atr_val * 3 if direction == "LONG" else price - atr_val * 3

    qty = position_size(price, sl)

    positions[symbol] = {
        "dir": direction,
        "entry": price,
        "sl": sl,
        "tp": tp,
        "qty": qty
    }

    send(f"""🚀 NEW TRADE {symbol}
Dir: {direction}
Entry: {round(price,2)}
TP: {round(tp,2)}
SL: {round(sl,2)}
Qty: {qty}
Risk: %{RISK_PERCENT}
""")

def manage_trade(symbol, price):
    pos = positions[symbol]

    if pos["dir"] == "LONG":
        if price >= pos["tp"]:
            send(f"🎯 TP HIT {symbol}")
            del positions[symbol]
        elif price <= pos["sl"]:
            send(f"❌ SL HIT {symbol}")
            del positions[symbol]

    elif pos["dir"] == "SHORT":
        if price <= pos["tp"]:
            send(f"🎯 TP HIT {symbol}")
            del positions[symbol]
        elif price >= pos["sl"]:
            send(f"❌ SL HIT {symbol}")
            del positions[symbol]

def signal(symbol):
    df5 = get_data(symbol,"5m")
    df15 = get_data(symbol,"15m")

    sw = sweep(df5)
    tr = trend(df15)
    vol = volume(df5)
    mom = momentum(df5)

    atr_val = atr(df5).iloc[-1]
    price = df5["close"].iloc[-1]

    score = 0
    if sw: score += 40
    if tr: score += 20
    if vol: score += 20
    if mom: score += 20

    print(symbol,"Score:",score,"Pos:",symbol in positions)

    # açık trade varsa yönet
    if symbol in positions:
        manage_trade(symbol, price)
        return

    # ENTRY
    if sw or (score >= 40 and vol and mom):
        direction = sw if sw else "LONG"
        open_trade(symbol, direction, price, atr_val)

def run():
    send("🚀 V71 TRADE ENGINE AKTİF")

    while True:
        try:
            for s in symbols:
                signal(s)
                time.sleep(1)
            time.sleep(20)
        except Exception as e:
            print("HATA:", e)
            time.sleep(5)

if __name__ == "__main__":
    run()
