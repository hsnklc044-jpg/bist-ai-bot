import os
import requests

from engine.ultimate_scanner import run_ultimate_scan

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def send_telegram_message(message):

    url = f"{BASE_URL}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        requests.post(url, json=payload)

    except Exception as e:
        print("Telegram gönderim hatası:", e)


def get_updates(offset=None):

    url = f"{BASE_URL}/getUpdates"

    params = {"timeout": 100}

    if offset:
        params["offset"] = offset

    r = requests.get(url, params=params)

    return r.json()


def handle_command(text):

    if text == "/help":

        return """
Komutlar:

/radar → anlık radar taraması
/top → en güçlü hisseler
/support HİSSE → destek direnç
"""

    if text == "/radar":

        signals = run_ultimate_scan()

        if not signals:
            return "Sinyal bulunamadı."

        return "\n\n".join(signals)

    if text == "/top":

        signals = run_ultimate_scan()

        if not signals:
            return "Güçlü hisse yok."

        return "\n\n".join(signals[:3])

    if text.startswith("/support"):

        return "Support/Resistance modülü yakında eklenecek."

    return "Komut tanınmadı. /help yaz."


def listen_commands():

    print("🤖 Telegram komut dinleyici başladı")

    offset = None

    while True:

        updates = get_updates(offset)

        for update in updates["result"]:

            offset = update["update_id"] + 1

            try:

                text = update["message"]["text"]

                response = handle_command(text)

                send_telegram_message(response)

            except:
                pass
