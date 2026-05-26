import asyncio
import websockets
import json
import requests
import time

BOT_TOKEN = "8434925197:AAEzOTp4Q0zjRSlcHjQg8Mj9tvagXZHN1uI"
CHAT_ID = "1790584407"

USERNAME = "52558373020"
PASSWORD = "44Dupduru"

SYMBOLS = ["ASELS", "THYAO"]


def send(msg):
    print("TELEGRAM:", msg)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# 🔐 LOGIN (örnek endpoint)
def login():
    url = "https://api.gedik.com/auth/login"

    payload = {
        "username": USERNAME,
        "password": PASSWORD
    }

    r = requests.post(url, json=payload)

    try:
        token = r.json()["token"]
        print("✅ TOKEN ALINDI")
        return token
    except:
        print("❌ LOGIN FAIL:", r.text)
        return None


# 🚀 WEBSOCKET
async def run_ws(token):

    ws_url = "wss://ws.gedik.com/market"

    async with websockets.connect(ws_url) as ws:

        print("🔌 WS BAĞLANDI")

        # 🔐 AUTH
        await ws.send(json.dumps({
            "type": "auth",
            "token": token
        }))

        # 📡 ABONE OL
        await ws.send(json.dumps({
            "type": "subscribe",
            "symbols": SYMBOLS
        }))

        last_prices = {}

        while True:

            data = await ws.recv()
            msg = json.loads(data)

            # 🔥 ÖRNEK FORMAT
            if "symbol" in msg and "price" in msg:

                symbol = msg["symbol"]
                price = msg["price"]

                print(symbol, price)

                if symbol not in last_prices:
                    last_prices[symbol] = price
                    continue

                # 💣 SADE FİLTRE
                if abs(price - last_prices[symbol]) >= 0.25:

                    send(f"📊 {symbol} | {price}")

                    last_prices[symbol] = price


def main():

    send("🚀 GEDIK BOT BAŞLADI")

    token = login()

    if not token:
        return

    asyncio.run(run_ws(token))


if __name__ == "__main__":
    main()