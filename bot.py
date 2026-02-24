import os
import requests
from flask import Flask

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_message():
    if not TOKEN or not CHAT_ID:
        return "Env eksik"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": "🚀 ZAMANLANMIŞ TEST MESAJI"
    }

    requests.post(url, json=payload)
    return "Mesaj gönderildi"


@app.route("/")
def home():
    return "Bot aktif."


@app.route("/send")
def trigger():
    return send_message()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
