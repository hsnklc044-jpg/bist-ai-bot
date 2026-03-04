import os
import requests
import time
import threading

from engine.ultimate_scanner import run_ultimate_scan
from engine.support_resistance_engine import get_support_resistance


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


# ---------------------------------------------------
# TELEGRAM MESSAGE
# ---------------------------------------------------

def send_message(text):

    try:

        url = f"{BASE_URL}/sendMessage"

        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }

        requests.post(url, json=payload)

    except Exception as e:

        print("Telegram send error:", e)


# ---------------------------------------------------
# RADAR
# ---------------------------------------------------

def radar():

    print("🚀 Radar başlatıldı")

    try:

        signals = run_ultimate_scan()

        if not signals:

            send_message("Sinyal bulunamadı.")
            return

        for signal in signals[:5]:

            text = f"""
📊 <b>{signal['symbol']}</b>

Fiyat: {signal['price']}

Skor: {signal['score']}

🎯 Hedef: {signal['target']}
🛑 Stop: {signal['stop']}
"""

            send_message(text)

    except Exception as e:

        print("Radar error:", e)

        send_message("Radar çalışırken hata oluştu.")


# ---------------------------------------------------
# COMMAND LISTENER
# ---------------------------------------------------

def listen_commands():

    print("📡 Telegram komutları dinleniyor...")

    offset = None

    while True:

        try:

            url = f"{BASE_URL}/getUpdates"

            params = {}

            if offset:
                params["offset"] = offset

            response = requests.get(url, params=params).json()

            # KeyError fix
            if "result" not in response:
                time.sleep(2)
                continue

            updates = response["result"]

            for update in updates:

                offset = update["update_id"] + 1

                if "message" not in update:
                    continue

                message = update["message"]

                if "text" not in message:
                    continue

                text = message["text"]

                # -------------------------
                # RADAR
                # -------------------------

                if text.startswith("/radar"):

                    radar()

                # -------------------------
                # SUPPORT
                # -------------------------

                elif text.startswith("/support"):

                    parts = text.split()

                    if len(parts) < 2:

                        send_message("Kullanım: /support THYAO")
                        continue

                    symbol = parts[1].upper()

                    result = get_support_resistance(symbol)

                    send_message(result)

        except Exception as e:

            print("Command listener error:", e)

        time.sleep(2)


# ---------------------------------------------------
# THREAD START
# ---------------------------------------------------

def start_bot():

    thread = threading.Thread(target=listen_commands)

    thread.start()


# ---------------------------------------------------

if __name__ == "__main__":

    print("🤖 BIST AI BOT BAŞLADI")

    start_bot()

    while True:

        time.sleep(60)
