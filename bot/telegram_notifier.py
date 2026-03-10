import requests

BOT_TOKEN = "8772282578:AAHayduiZtDuf659L0Fx9H8ehOcn81tii10"
CHAT_ID = "1790584407"


def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=payload)
    except:
        pass