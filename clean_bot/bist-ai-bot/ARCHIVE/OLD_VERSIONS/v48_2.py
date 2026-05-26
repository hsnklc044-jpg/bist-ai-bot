import requests
import pandas as pd
import time
import hmac
import hashlib
import math
from datetime import date

API_KEY = "eTav5oGlcYvGO151lVlDRmv77zn9z8RzZThI27eQv7qKAaVzxwI1FZ1vXtZZEZLg"
API_SECRET = "f8kNwWBFjyAU4AkuBNgnjtKG2tdkQoovIufVOXd9J2UDf0EpEyaczk6a3IOPUp5G"
BASE_URL = "https://testnet.binance.vision"

TELEGRAM_TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"

COINS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","AVAXUSDT"]

RISK_PERCENT = 0.02
MAX_CONSEC_LOSS = 3

in_position = False
position_side = None
entry_price = 0
max_profit_price = 0
active_symbol = None
position_qty = 0

wins = 0
losses = 0
consec_loss = 0
last_report_day = date.today()
last_heartbeat = 0

def send_telegram(msg):
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                  data={"chat_id": CHAT_ID, "text": msg})

def get_price(symbol):
    return float(requests.get(BASE_URL + f"/api/v3/ticker/price?symbol={symbol}").json()['price'])

def get_balance():
    params = {"timestamp": int(time.time()*1000)}
    query = "&".join([f"{k}={v}" for k,v in params.items()])
    sig = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    headers = {"X-MBX-APIKEY": API_KEY}
    res = requests.get(BASE_URL + f"/api/v3/account?{query}&signature={sig}", headers=headers).json()
    for b in res.get("balances", []):
        if b["asset"] == "USDT":
            return float(b["free"])
    return 0

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
    balance = get_balance()
    risk_usdt = balance * RISK_PERCENT
    price = get_price(symbol)
    raw = risk_usdt / price
    step = get_step(symbol)
    qty = math.floor(raw / step) * step
    return float(format_qty(qty, step))

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
        "quantity": str(quantity),
        "timestamp": int(time.time() * 1000)
    }

    params["signature"] = sign(params)
    headers = {"X-MBX-APIKEY": API_KEY}

    res = requests.post(BASE_URL + "/api/v3/order", headers=headers, params=params).json()

    return "status" in res

print("V48.2 HEARTBEAT BOT BASLADI...")

while True:
    try:

        # 🔥 HEARTBEAT
        if time.time() - last_heartbeat > 60:
            send_telegram("⏸ SYSTEM ACTIVE\nTarama devam ediyor...")
            last_heartbeat = time.time()

        best = None
        for coin in COINS:
            r = analyze(coin)
            if r and (not best or r["strength"] > best["strength"]):
                best = r

        if not in_position and best:

            in_position = True

            symbol = best["symbol"]
            signal = best["signal"]
            qty = calculate_qty(symbol)

            if qty <= 0:
                in_position = False
                continue

            ok = place_order(symbol, signal, qty)

            if ok:
                position_side = signal
                entry_price = get_price(symbol)
                max_profit_price = entry_price
                active_symbol = symbol
                position_qty = qty

                send_telegram(f"🚀 ENTRY\n{symbol}\n{signal}\nQty:{qty}")
            else:
                in_position = False
                send_telegram("❌ ORDER FAIL")

        elif in_position:

            price = get_price(active_symbol)

            if position_side == "BUY":
                max_profit_price = max(max_profit_price, price)

                if price <= entry_price * 0.98 or price <= max_profit_price * 0.99:
                    place_order(active_symbol, "SELL", position_qty)
                    send_telegram(f"EXIT {active_symbol}")
                    in_position = False

            elif position_side == "SELL":
                max_profit_price = min(max_profit_price, price)

                if price >= entry_price * 1.02 or price >= max_profit_price * 1.01:
                    place_order(active_symbol, "BUY", position_qty)
                    send_telegram(f"EXIT {active_symbol}")
                    in_position = False

        time.sleep(15)

    except Exception as e:
        send_telegram(f"HATA {str(e)}")
        time.sleep(10)
