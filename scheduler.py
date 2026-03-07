import requests
import time
import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

def run_bot():
    send_telegram("BIST AI Bot aktif 🚀")

if __name__ == "__main__":
    while True:
        run_bot()
        time.sleep(3600)
