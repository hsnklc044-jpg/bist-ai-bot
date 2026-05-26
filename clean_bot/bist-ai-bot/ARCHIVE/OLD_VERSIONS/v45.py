import requests
import pandas as pd
import time
import hmac
import hashlib

API_KEY = "eTav5oGlcYvGO151lVlDRmv77zn9z8RzZThI27eQv7qKAaVzxwI1FZ1vXtZZEZLg"
API_SECRET = "f8kNwWBFjyAU4AkuBNgnjtKG2tdkQoovIufVOXd9J2UDf0EpEyaczk6a3IOPUp5G"
BASE_URL = "https://testnet.binance.vision"

TELEGRAM_TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"

SYMBOL = "BTCUSDT"

in_position = False
entry_price = 0

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_price():
    url = BASE_URL + f"/api/v3/ticker/price?symbol={SYMBOL}"
    return float(requests.get(url).json()['price'])

def get_signal():
    url = BASE_URL + f"/api/v3/klines?symbol={SYMBOL}&interval=1m&limit=50"
    data = requests.get(url).json()

    df = pd.DataFrame(data)
    df[4] = df[4].astype(float)

    df['ma20'] = df[4].rolling(20).mean()
    df['ma50'] = df[4].rolling(50).mean()

    if df['ma20'].iloc[-1] > df['ma50'].iloc[-1]:
        return "BUY"
    elif df['ma20'].iloc[-1] < df['ma50'].iloc[-1]:
        return "SELL"
    return "HOLD"

def sign(params):
    query = "&".join([f"{k}={v}" for k,v in params.items()])
    return hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()

def place_order(side, quantity):
    endpoint = "/api/v3/order"
    params = {
        "symbol": SYMBOL,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
        "timestamp": int(time.time() * 1000)
    }

    params["signature"] = sign(params)

    headers = {"X-MBX-APIKEY": API_KEY}
    r = requests.post(BASE_URL + endpoint, headers=headers, params=params)
    return r.json()

def qty():
    return "0.001"

print("V45 BOT BASLADI...")

last_signal = None

while True:
    try:
        signal = get_signal()
        price = get_price()

        print(f"SINYAL: {signal} | PRICE: {price}")

        # ===== POZİSYON YOKSA =====
        if not in_position:

            if signal == "BUY" and signal != last_signal:
                order = place_order("BUY", qty())
                entry_price = price
                in_position = True
                send_telegram(f"🟢 BUY\nFiyat: {price}\nOrder: {order}")

        # ===== POZİSYON VARSA =====
        else:
            sl = entry_price * 0.98
            tp = entry_price * 1.02

            if price <= sl:
                order = place_order("SELL", qty())
                in_position = False
                send_telegram(f"🔴 STOP LOSS\nFiyat: {price}\nOrder: {order}")

            elif price >= tp:
                order = place_order("SELL", qty())
                in_position = False
                send_telegram(f"🟢 TAKE PROFIT\nFiyat: {price}\nOrder: {order}")

        last_signal = signal
        time.sleep(10)

    except Exception as e:
        print("HATA:", e)
        send_telegram(f"❌ HATA {str(e)}")
        time.sleep(10)
