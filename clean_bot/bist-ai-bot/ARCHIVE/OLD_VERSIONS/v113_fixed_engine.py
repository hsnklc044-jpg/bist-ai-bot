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
    except Exception as e:
        print("TELEGRAM ERROR:", e)

SYMBOLS = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

open_trade = None
cooldown = {}

# =========================
# DATA
# =========================
def get_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=100"
        data = requests.get(url, timeout=10).json()

        df = pd.DataFrame(data)
        df = df.iloc[:,0:6]
        df.columns = ["time","open","high","low","close","volume"]
        df = df.astype(float)

        return df
    except Exception as e:
        print("DATA ERROR:", e)
        return None

def ema(df):
    df['ema'] = df['close'].ewm(span=50).mean()
    return df

# =========================
# SIGNAL
# =========================
def signal(df, symbol):
    df = ema(df)
    last = df.iloc[-1]

    # TREND FILTER (sideways engelle)
    distance = abs(last['close'] - last['ema']) / last['ema']

    if distance < 0.001:
        return None

    trend = "UP" if last['close'] > last['ema'] else "DOWN"

    if trend == "UP" and last['close'] > last['open']:
        return "LONG"

    if trend == "DOWN" and last['close'] < last['open']:
        return "SHORT"

    return None

# =========================
# TRADE
# =========================
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

    send(f"🚨 {side} {symbol}\nEntry: {round(price,2)}")

def manage(df):
    global open_trade, cooldown

    if not open_trade:
        return

    price = df['close'].iloc[-1]
    entry = open_trade['entry']
    symbol = open_trade['symbol']

    # ======================
    # LONG
    # ======================
    if open_trade['side']=="LONG":

        if not open_trade['be'] and price > entry*1.005:
            open_trade['sl'] = entry
            open_trade['be'] = True
            send("🔒 BE LONG")

        if price > entry*1.01:
            open_trade['sl'] = max(open_trade['sl'], price*0.995)

        if price <= open_trade['sl']:
            send(f"❌ SL {symbol}")
            cooldown[symbol] = 3
            open_trade = None

        elif price >= open_trade['tp']:
            send(f"✅ TP {symbol}")
            open_trade = None

    # ======================
    # SHORT
    # ======================
    if open_trade and open_trade['side']=="SHORT":

        if not open_trade['be'] and price < entry*0.995:
            open_trade['sl'] = entry
            open_trade['be'] = True
            send("🔒 BE SHORT")

        if price < entry*0.99:
            open_trade['sl'] = min(open_trade['sl'], price*1.005)

        if price >= open_trade['sl']:
            send(f"❌ SL {symbol}")
            cooldown[symbol] = 3
            open_trade = None

        elif price <= open_trade['tp']:
            send(f"✅ TP {symbol}")
            open_trade = None

# =========================
# MAIN
# =========================
def run():
    send("🔥 V113 FIX BAŞLADI")

    while True:
        for s in SYMBOLS:

            print("CHECK:", s)

            # ✅ FIXED COOLDOWN
            if s in cooldown:
                cooldown[s] -= 1
                if cooldown[s] <= 0:
                    del cooldown[s]
                else:
                    continue

            df = get_data(s)
            if df is None:
                continue

            manage(df)

            if open_trade:
                continue

            sig = signal(df, s)

            if sig:
                price = df['close'].iloc[-1]
                open_new(s, price, sig)

        time.sleep(60)

if __name__ == "__main__":
    run()