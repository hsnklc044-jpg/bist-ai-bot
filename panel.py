import os
from ai_signal_engine import find_best_signals
from flask import Flask, request
import requests

app = Flask(__name__)

PANEL_PASSWORD = os.getenv("44Dupduru--")
TELEGRAM_TOKEN = os.getenv("8507109549:AAHIc8UaN0CboGSzji0S6xfC8D7l2hls2AA")



# Ana sayfa (panel çalışıyor mu testi)
@app.route("/")
def home():
    return "📊 BIST AI PANEL AKTİF\nBot başarıyla çalışıyor."


# TELEGRAM WEBHOOK
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    # DEBUG LOG
    print("GELEN DATA:", data)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # DEBUG LOG
        print("CHAT ID:", chat_id)
        print("MESAJ:", text)

        if text == "/start":
    send_telegram(chat_id, "🤖 BIST AI aktif.\nSinyaller hazırlanıyor...")

    signals = find_best_signals()

    if not signals:
        send_telegram(chat_id, "Bugün güçlü sinyal bulunamadı.")
    else:
        msg = "📊 GÜNÜN EN GÜÇLÜ HİSSELERİ\n\n"
        for s, score in signals:
            msg += f"{s} → Güç Skoru: {score}\n"

        send_telegram(chat_id, msg)

        else:
            send_telegram(chat_id, "Komut alındı: " + text)

    return "ok", 200


def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post(url, json=payload)

    # TELEGRAM CEVABI LOG
    print("TELEGRAM RESPONSE:", response.text)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render için doğru port
    app.run(host="0.0.0.0", port=port)
