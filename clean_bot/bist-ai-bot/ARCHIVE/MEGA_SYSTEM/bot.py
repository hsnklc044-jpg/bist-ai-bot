import asyncio
import numpy as np
import requests
from binance.client import Client

# ==============================
# CONFIG
# ==============================

API_KEY = "API_KEYİN"
API_SECRET = "SECRETİN"

TELEGRAM_TOKEN = "BOT_TOKEN"
CHAT_ID = "CHAT_ID"

client = Client(API_KEY, API_SECRET)
client.API_URL = "https://testnet.binance.vision/api"

SYMBOL = "BTCUSDT"
TRADE_USDT = 20

POSITION = None
COOLDOWN = 300
last_trade_time = 0

# ==============================
# TELEGRAM
# ==============================

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg
    })

# ==============================
# DATA
# ==============================

def get_klines():
    k = client.get_klines(symbol=SYMBOL, interval="1m", limit=100)
    return [float(x[4]) for x in k]

# ==============================
# INDICATORS
# ==============================

def rsi(prices):
    d = np.diff(prices)
    g = np.where(d > 0, d, 0)
    l = np.where(d < 0, -d, 0)
    ag = np.mean(g[-14:])
    al = np.mean(l[-14:])
    if al == 0:
        return 100
    rs = ag / al
    return 100 - (100 / (1 + rs))


def ema(data, p):
    a = 2 / (p + 1)
    e = [data[0]]
    for price in data[1:]:
        e.append(a * price + (1 - a) * e[-1])
    return e


def macd(prices):
    e12 = ema(prices, 12)
    e26 = ema(prices, 26)
    m = np.array(e12[-len(e26):]) - np.array(e26)
    s = ema(m.tolist(), 9)
    return m[-1], s[-1]

# ==============================
# TRADE
# ==============================

def buy(price):
    global POSITION
    qty = round(TRADE_USDT / price, 5)

    client.order_market_buy(symbol=SYMBOL, quantity=qty)

    POSITION = {
        "entry": price,
        "qty": qty,
        "stop": price * 0.97,
        "tp": price * 1.04,
        "trail": price
    }

    send(f"🟢 BUY\nFiyat: {price}")


def sell(price, reason):
    global POSITION
    qty = POSITION["qty"]

    client.order_market_sell(symbol=SYMBOL, quantity=qty)

    pnl = (price - POSITION["entry"]) / POSITION["entry"] * 100

    send(f"🔴 SELL ({reason})\nFiyat: {price}\nPnL: %{round(pnl,2)}")

    POSITION = None

# ==============================
# ENGINE
# ==============================

async def engine():
    global last_trade_time

    send("🤖 BOT BAŞLADI")

    while True:
        try:
            prices = get_klines()
            price = prices[-1]

            r = rsi(prices)
            m, s = macd(prices)

            print(f"{price} RSI:{r:.2f}")

            now = asyncio.get_event_loop().time()

            if now - last_trade_time < COOLDOWN:
                await asyncio.sleep(5)
                continue

            if POSITION is None:
                if r < 35 and m > s:
                    buy(price)
                    last_trade_time = now
            else:
                if price > POSITION["trail"]:
                    POSITION["trail"] = price

                if price <= POSITION["stop"]:
                    sell(price, "STOP")
                    last_trade_time = now

                elif price >= POSITION["tp"]:
                    sell(price, "TP")
                    last_trade_time = now

                elif price < POSITION["trail"] * 0.98:
                    sell(price, "TRAIL")
                    last_trade_time = now

        except Exception as e:
            print("ERROR:", e)

        await asyncio.sleep(10)

# ==============================
# START
# ==============================

if __name__ == "__main__":
    asyncio.run(engine())