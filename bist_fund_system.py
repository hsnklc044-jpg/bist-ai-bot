import os
import requests

# GitHub Secrets'tan alınır
TELEGRAM_TOKEN = os.getenv("8440357756:AAGdYajs2PirEhY2O9R8Voe_JmtAQhIHI8I")
TELEGRAM_CHAT_ID = os.getenv("1790584407")


# -----------------------------
# TEST MESAJI GÖNDERME FONKSİYONU
# -----------------------------
def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik.")
        return

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }

        r = requests.post(url, data=payload, timeout=10)
        print("Telegram cevap:", r.text)

    except Exception as e:
        print("Telegram gönderilemedi:", e)


# -----------------------------
# ANA ÇALIŞMA
# -----------------------------
def main():
    print("AI Fon Yöneticisi çalıştı.")

    # Basit test mesajı
    mesaj = "📊 GITHUB → TELEGRAM TEST BAŞARILI"

    # Telegram’a gönder
    send_telegram(mesaj)


# -----------------------------
# ÇALIŞTIRMA
# -----------------------------
if __name__ == "__main__":
    print("TOKEN:", TELEGRAM_TOKEN)
    print("CHAT_ID:", TELEGRAM_CHAT_ID)
    main()
