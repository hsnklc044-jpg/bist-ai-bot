import os
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def run():

    if not TOKEN or not CHAT_ID:
        print("Environment değişkenleri eksik.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": "🚀 BOT TEMİZ KURULUM TEST MESAJI"
    }

    response = requests.post(url, json=payload)

    print(response.text)


if __name__ == "__main__":
    run()
