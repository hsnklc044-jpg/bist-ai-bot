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
position_side = None
entry_price = 0
max_profit_price = 0

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_price():
    url = BASE_URL + f"/api/v3/ticker/price?symbol={SYMBOL}"
    return float(requests.get(url).json()['price'])

def get_data():
    url = BASE_URL + f"/api/v3/klines?symbol={SYMBOL}&interval=1m&limit=50"
    return pd.DataFrame(requests.get(url).json())

def get_signal():
    df = get_data()
    df[4] = df[4].astype(float)
    df[5] = df[5].astype(float)

    df['ma20'] = df[4].rolling(20).mean()
    df['ma50'] = df[4].rolling(50).mean()

    volume_mean = df[5].rolling(20).mean().iloc[-1]
    volume_now = df[5].iloc[-1]

    if volume_now < volume_mean:
        return "HOLD", volume_now, volume_mean

    if df['ma20'].iloc[-1] > df['ma50'].iloc[-1]:
        return "BUY", volume_now, volume_mean
    elif df['ma20'].iloc[-1] < df['ma50'].iloc[-1]:
        return "SELL", volume_now, volume_mean

    return "HOLD", volume_now, volume_mean

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
    res = requests.post(BASE_URL + endpoint, headers=headers, params=params).json()

    # 🔥 ORDER KONTROL
    if "status" in res:
        return True, res
    else:
        return False, res

def qty():
    return "0.001"

print("V46.2 BOT BASLADI...")

last_signal = None
last_info_time = 0

while True:
    try:
        signal, vol_now, vol_mean = get_signal()
        price = get_price()

        print(f"SINYAL: {signal} | PRICE: {price}")

        # 🔥 HOLD BİLGİ MESAJI (60 sn'de 1)
        if signal == "HOLD" and time.time() - last_info_time > 60:
            send_telegram(f"⏸ HOLD\nFiyat: {price}\nHacim: {round(vol_now,2)} < {round(vol_mean,2)}")
            last_info_time = time.time()

        # ===== GİRİŞ =====
        if not in_position and signal != last_signal:

            if signal == "BUY":
                ok, order = place_order("BUY", qty())
                if ok:
                    entry_price = price
                    max_profit_price = price
                    in_position = True
                    position_side = "LONG"
                    send_telegram(f"🟢 LONG ENTRY\n{price}")
                else:
                    send_telegram(f"❌ ORDER FAIL\n{order}")

            elif signal == "SELL":
                ok, order = place_order("SELL", qty())
                if ok:
                    entry_price = price
                    max_profit_price = price
                    in_position = True
                    position_side = "SHORT"
                    send_telegram(f"🔴 SHORT ENTRY\n{price}")
                else:
                    send_telegram(f"❌ ORDER FAIL\n{order}")

        # ===== POZİSYON =====
        elif in_position:

            if position_side == "LONG":
                max_profit_price = max(max_profit_price, price)

                if price <= entry_price * 0.98 or price <= max_profit_price * 0.99:
                    ok, _ = place_order("SELL", qty())
                    if ok:
                        send_telegram(f"EXIT LONG {price}")
                        in_position = False
                        position_side = None

            elif position_side == "SHORT":
                max_profit_price = min(max_profit_price, price)

                if price >= entry_price * 1.02 or price >= max_profit_price * 1.01:
                    ok, _ = place_order("BUY", qty())
                    if ok:
                        send_telegram(f"EXIT SHORT {price}")
                        in_position = False
                        position_side = None

        last_signal = signal
        time.sleep(10)

    except Exception as e:
        print("HATA:", e)
        send_telegram(f"HATA {str(e)}")
        time.sleep(10)
