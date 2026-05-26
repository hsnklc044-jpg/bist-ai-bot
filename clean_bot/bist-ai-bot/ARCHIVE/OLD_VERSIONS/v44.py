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

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
        print("TELEGRAM:", r.text)
    except Exception as e:
        print("TELEGRAM HATA:", e)

def get_signal():
    url = BASE_URL + "/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=50"
    data = requests.get(url).json()

    df = pd.DataFrame(data)
    df[4] = df[4].astype(float)

    df['ma20'] = df[4].rolling(20).mean()
    df['ma50'] = df[4].rolling(50).mean()

    if df['ma20'].iloc[-1] > df['ma50'].iloc[-1]:
        return "BUY"
    elif df['ma20'].iloc[-1] < df['ma50'].iloc[-1]:
        return "SELL"
    else:
        return "HOLD"

def sign(params):
    query = "&".join([f"{k}={v}" for k,v in params.items()])
    return hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()

# 🔥 SABİT VE GEÇERLİ LOT (HATA YOK)
def calculate_qty():
    return "0.001"

def place_order(side, quantity):
    endpoint = "/api/v3/order"

    params = {
        "symbol": "BTCUSDT",
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
        "timestamp": int(time.time() * 1000)
    }

    params["signature"] = sign(params)

    headers = {
        "X-MBX-APIKEY": API_KEY
    }

    response = requests.post(BASE_URL + endpoint, headers=headers, params=params)
    return response.json()

print("BOT BASLADI...")

last_signal = None

while True:
    try:
        signal = get_signal()
        print("SINYAL:", signal)

        if signal != last_signal or last_signal is None:

            print("ISLEM:", signal)
            qty = calculate_qty()

            if signal == "BUY":
                order = place_order("BUY", qty)
                send_telegram(f"BUY EMIR {order}")

            elif signal == "SELL":
                order = place_order("SELL", qty)
                send_telegram(f"SELL EMIR {order}")

            else:
                send_telegram(f"SINYAL: {signal}")

            last_signal = signal

        time.sleep(10)

    except Exception as e:
        print("HATA:", e)
        send_telegram(f"HATA {str(e)}")
        time.sleep(10)
