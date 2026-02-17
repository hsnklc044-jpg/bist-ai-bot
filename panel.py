import os
from flask import Flask, request
import requests

# Eğer AI sinyal motorun varsa bunu kullanacak
try:
    from ai_signal_engine import find_best_signals
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

app = Flask(__name__)

# ENV değişkenleri
TELEGRAM_TOKEN = os.getenv("8507109549:AAEj56EhY_-_B8Om4QA_rvqaU0QsqeYEdtc")
CHAT_ID = os.getenv("1790584407")

# ---------------------------------------------------
# Ana sayfa kontrol
# ---------------------------------------------------
@app.route("/")
def home():
    return "📊 BIST AI PANEL AKTİF\nSunucu çalışıyor."

# ---------------------------------------------------
# Telegram mesaj gönderme
# ---------------------------------------------------
def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    requests.post(url, json=payload, timeout=10)

# ---------------------------------------------------
# /start komutu AI başlatır
# ---------------------------------------------------
def handle_start(chat_id):
    send_telegram(
        chat_id,
        "🤖 BIST AI aktif.\n"
        "Sinyaller hazırlanıyor...\n\n"
        "⏳ Lütfen bekleyin..."
    )

    # AI motoru varsa çalıştır
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

        except Exception as e:
            send_telegram(chat_id, "AI sinyal motorunda hata oluştu.")
    else:
        send_telegram(
            chat_id,
            "AI sinyal motoru henüz bağlı değil.\n"
            "Kurulum sonrası otomatik çalışacak."
        )

# ---------------------------------------------------
# Telegram Webhook
# ---------------------------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            handle_start(chat_id)
        else:
            send_telegram(chat_id, f"Komut alındı: {text}")

    return "ok", 200

# ---------------------------------------------------
# Render port ayarı
# ---------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
