import os
from flask import Flask, request
import requests

# AI motoru varsa kullan
try:
    from ai_signal_engine import find_best_signals
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

# Flask uygulaması
app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("8507109549:AAEj56EhY_-_B8Om4QA_rvqaU0QsqeYEdtc")


# ---------------------------------------------------
# Ana sayfa
# ---------------------------------------------------
@app.route("/")
def home():
    return "📊 BIST AI PANEL AKTİF"


# ---------------------------------------------------
# Telegram mesaj gönder
# ---------------------------------------------------
def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=10)


# ---------------------------------------------------
# /start komutu
# ---------------------------------------------------
def handle_start(chat_id):
    send_telegram(chat_id, "🤖 BIST AI aktif.\nSinyaller hazırlanıyor...")

    if AI_AVAILABLE:
        try:
            signals = find_best_signals()

            if not signals:
                send_telegram(chat_id, "Bugün güçlü sinyal bulunamadı.")
                return

            text = "📊 GÜNÜN EN GÜÇLÜ HİSSELERİ\n\n"
            for s in signals[:5]:
                text += f"• {s['symbol']} → Skor: {s['score']}\n"

            send_telegram(chat_id, text)

        except Exception:
            send_telegram(chat_id, "AI sinyal motorunda hata oluştu.")
    else:
        send_telegram(chat_id, "AI motoru henüz bağlı değil.")


# ---------------------------------------------------
# Webhook
# ---------------------------------------------------
@app.route("/webhook", methods=["POST", "GET"])
def webhook():

    # GET testi
    if request.method == "GET":
        return "Webhook aktif", 200

    data = request.get_json(silent=True)

    if not data:
        return "No JSON", 200

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            handle_start(chat_id)
        else:
            send_telegram(chat_id, f"Komut alındı: {text}")

    return "ok", 200


# ---------------------------------------------------
# Render port
# ---------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
