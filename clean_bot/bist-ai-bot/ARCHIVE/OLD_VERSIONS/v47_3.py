import requests
import pandas as pd
import time
import hmac
import hashlib
import math

API_KEY = "eTav5oGlcYvGO151lVlDRmv77zn9z8RzZThI27eQv7qKAaVzxwI1FZ1vXtZZEZLg"
API_SECRET = "f8kNwWBFjyAU4AkuBNgnjtKG2tdkQoovIufVOXd9J2UDf0EpEyaczk6a3IOPUp5G"
BASE_URL = "https://testnet.binance.vision"

TELEGRAM_TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"

COINS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","AVAXUSDT"]

USDT_AMOUNT = 20

in_position = False
position_side = None
entry_price = 0
max_profit_price = 0
active_symbol = None

def send_telegram(msg):
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                  data={"chat_id": CHAT_ID, "text": msg})

def get_price(symbol):
    return float(requests.get(BASE_URL + f"/api/v3/ticker/price?symbol={symbol}").json()['price'])

def get_step(symbol):
    info = requests.get(BASE_URL + "/api/v3/exchangeInfo").json()
    for s in info["symbols"]:
        if s["symbol"] == symbol:
            for f in s["filters"]:
                if f["filterType"] == "LOT_SIZE":
                    return float(f["stepSize"])
    return 0.00001

def format_qty(qty, step):
    precision = int(round(-math.log(step, 10), 0))
    return round(qty, precision)

def calculate_qty(symbol):
    price = get_price(symbol)
    raw = USDT_AMOUNT / price
    step = get_step(symbol)
    qty = math.floor(raw / step) * step
    return str(format_qty(qty, step))

def get_data(symbol):
    return pd.DataFrame(requests.get(BASE_URL + f"/api/v3/klines?symbol={symbol}&interval=1m&limit=50").json())

def analyze(symbol):
    df = get_data(symbol)
    df[4] = df[4].astype(float)
    df[5] = df[5].astype(float)

    df['ma20'] = df[4].rolling(20).mean()
    df['ma50'] = df[4].rolling(50).mean()

    vol_mean = df[5].rolling(20).mean().iloc[-1]
    vol_now = df[5].iloc[-1]

    if vol_now < vol_mean:
        return None

    strength = vol_now / vol_mean

    if df['ma20'].iloc[-1] > df['ma50'].iloc[-1]:
        return {"symbol": symbol, "signal": "BUY", "strength": strength}
    elif df['ma20'].iloc[-1] < df['ma50'].iloc[-1]:
        return {"symbol": symbol, "signal": "SELL", "strength": strength}

    return None

def sign(params):
    query = "&".join([f"{k}={v}" for k,v in params.items()])
    return hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()

def place_order(symbol, side, quantity):
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
        "timestamp": int(time.time() * 1000)
    }

    params["signature"] = sign(params)
    headers = {"X-MBX-APIKEY": API_KEY}

    res = requests.post(BASE_URL + "/api/v3/order", headers=headers, params=params).json()

    if "status" in res:
        return True, res
    return False, res

print("V47.3 FINAL BASLADI...")

while True:
    try:
        best = None

        for coin in COINS:
            r = analyze(coin)
            if r and (not best or r["strength"] > best["strength"]):
                best = r

        if not in_position and best:

            symbol = best["symbol"]
            signal = best["signal"]
            qty = calculate_qty(symbol)

            ok, _ = place_order(symbol, signal, qty)

            if ok:
                in_position = True
                position_side = signal
                entry_price = get_price(symbol)
                max_profit_price = entry_price
                active_symbol = symbol

                send_telegram(f"🚀 ENTRY {symbol} {signal} Qty:{qty}")

        elif in_position:

            price = get_price(active_symbol)

            if position_side == "BUY":
                max_profit_price = max(max_profit_price, price)
                if price <= entry_price * 0.98 or price <= max_profit_price * 0.99:
                    place_order(active_symbol, "SELL", calculate_qty(active_symbol))
                    send_telegram(f"EXIT LONG {active_symbol}")
                    in_position = False

            elif position_side == "SELL":
                max_profit_price = min(max_profit_price, price)
                if price >= entry_price * 1.02 or price >= max_profit_price * 1.01:
                    place_order(active_symbol, "BUY", calculate_qty(active_symbol))
                    send_telegram(f"EXIT SHORT {active_symbol}")
                    in_position = False

        time.sleep(15)

    except Exception as e:
        send_telegram(f"HATA {str(e)}")
        time.sleep(10)
