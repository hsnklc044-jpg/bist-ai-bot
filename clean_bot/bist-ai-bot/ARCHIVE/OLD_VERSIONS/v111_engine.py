import pandas as pd
import time
import requests

BOT_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg}
        )
    except:
        pass

SYMBOLS = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]
INTERVAL = "5m"
LIMIT = 100

open_trade = None

def get_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={INTERVAL}&limit={LIMIT}"
        data = requests.get(url, timeout=10).json()

        df = pd.DataFrame(data)
        df = df.iloc[:,0:6]
        df.columns = ["time","open","high","low","close","volume"]
        df = df.astype(float)
        return df
    except:
        return None

def ema(df):
    df['ema'] = df['close'].ewm(span=50).mean()
    return df

def signal(df):
    df = ema(df)

    last = df.iloc[-1]
    trend = "UP" if last['close'] > last['ema'] else "DOWN"

    if trend == "UP" and last['close'] > last['open']:
        return "LONG"

    if trend == "DOWN" and last['close'] < last['open']:
        return "SHORT"

    return None

def open_new(symbol, price, side):
    global open_trade

    open_trade = {
        "symbol": symbol,
        "entry": price,
        "sl": price * 0.99 if side=="LONG" else price*1.01,
        "tp": price * 1.02 if side=="LONG" else price*0.98,
        "side": side,
        "be": False
    }

    send(f"🚨 {side} {symbol}\nEntry: {price}")

def manage(df):
    global open_trade

    if not open_trade:
        return

    price = df['close'].iloc[-1]

    entry = open_trade['entry']
    sl = open_trade['sl']
    tp = open_trade['tp']

    # BREAK EVEN
    if not open_trade['be']:
        if open_trade['side']=="LONG" and price > entry*1.005:
            open_trade['sl'] = entry
            open_trade['be'] = True
            send("🔒 BE AKTİF")

    # TRAILING
    if open_trade['side']=="LONG":
        if price > entry*1.01:
            open_trade['sl'] = max(open_trade['sl'], price*0.995)

    # EXIT
    if open_trade['side']=="LONG":
        if price <= open_trade['sl']:
            send("❌ SL")
            open_trade = None

        elif price >= open_trade['tp']:
            send("✅ TP")
            open_trade = None

def run():
    send("🔥 V111 BAŞLADI")

    while True:
        for s in SYMBOLS:
            df = get_data(s)
            if df is None:
                continue

            manage(df)

            if open_trade:
                continue

            sig = signal(df)

            if sig:
                price = df['close'].iloc[-1]
                open_new(s, price, sig)

        time.sleep(60)

if __name__ == "__main__":
    run()