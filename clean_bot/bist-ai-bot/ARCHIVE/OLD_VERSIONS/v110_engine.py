import pandas as pd
import time
import requests

# ================================
# TELEGRAM
# ================================

BOT_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
        print("TELEGRAM:", r.status_code, r.text)
    except Exception as e:
        print("TELEGRAM HATA:", e)

# ================================
# CONFIG
# ================================

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT", "BNBUSDT"]
INTERVAL = "5m"
LIMIT = 100

open_trades = []

# ================================
# DATA
# ================================

def get_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={INTERVAL}&limit={LIMIT}"
        data = requests.get(url, timeout=10).json()

        df = pd.DataFrame(data, columns=[
            "time","open","high","low","close","volume",
            "close_time","qav","trades","tbbav","tbqav","ignore"
        ])

        df = df[["open","high","low","close","volume"]].astype(float)
        return df
    except Exception as e:
        print("DATA ERROR:", e)
        return None

def ema(df):
    df['ema'] = df['close'].ewm(span=50).mean()
    return df

# ================================
# STRATEGY
# ================================

def generate_signal(df):
    df = ema(df)

    trend = "UP" if df['close'].iloc[-1] > df['ema'].iloc[-1] else "DOWN"
    last = df.iloc[-1]

    breakout = last['close'] > last['open']
    breakdown = last['close'] < last['open']

    if trend == "UP" and breakout:
        return "LONG"

    if trend == "DOWN" and breakdown:
        return "SHORT"

    return "NONE"

# ================================
# TRADE
# ================================

def has_open_trade():
    return len(open_trades) > 0

def open_trade(symbol, price, side):
    trade = {
        "symbol": symbol,
        "entry": price,
        "side": side
    }

    open_trades.append(trade)

    msg = f"🚨 TRADE\n{symbol}\n{side}\nEntry: {round(price,2)}"

    print("SENDING TELEGRAM...")
    send_telegram(msg)

# ================================
# MAIN
# ================================

def run():
    print("🚀 V110 ENGINE STARTED")

    # 🔥 START TEST
    send_telegram("🔥 BOT BAŞLADI")

    while True:
        for symbol in SYMBOLS:
            df = get_data(symbol)
            if df is None:
                continue

            if has_open_trade():
                continue

            signal = generate_signal(df)

            if signal != "NONE":
                price = df['close'].iloc[-1]
                open_trade(symbol, price, signal)

        time.sleep(60)

if __name__ == "__main__":
    run()