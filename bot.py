import os
import requests
from flask import Flask
from bist30 import scan_bist30

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_message(text):
    if not TOKEN or not CHAT_ID:
        return "Env eksik"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }

    requests.post(url, json=payload)


@app.route("/")
def home():
    return "Bot aktif."


@app.route("/send")
def trigger():
    send_message("🚀 ZAMANLANMIŞ TEST MESAJI")
    return "Mesaj gönderildi"


@app.route("/morning_scan")
def morning_scan():

    top3 = scan_bist30()

    if not top3:
        return "Veri bulunamadı"

    message = "🚀 BIST30 SABAH TARAMA\n\n"

    for i, stock in enumerate(top3, 1):
        message += f"{i}️⃣ {stock['symbol']} | RSI: {stock['rsi']} | Skor: {stock['score']}\n"

    send_message(message)

    return "Sabah tarama gönderildi"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
