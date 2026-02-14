import os
import requests

# GitHub Secrets'ten alınır
TELEGRAM_TOKEN = os.getenv("8440357756:AAGdYajs2PirEhY2O9R8Voe_JmtAQhIHI8I")
TELEGRAM_CHAT_ID = os.getenv("1790584407")


def send_telegram(message: str):
    """Telegram'a mesaj gönderir"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM ENV okunamadı")
        print("TOKEN:", TELEGRAM_TOKEN)
        print("CHAT_ID:", TELEGRAM_CHAT_ID)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    try:
        r = requests.post(url, data=payload, timeout=10)
        print("Telegram cevap:", r.text)
    except Exception as e:
        print("Telegram hata:", e)


def main():
    print("AI Fon Yöneticisi çalıştı")

    mesaj = (
        "📊 BIST AI BOT AKTİF\n\n"
        "Sistem başarıyla çalıştı.\n"
        "Bu bir test mesajıdır."
    )

    print(mesaj)
    send_telegram(mesaj)


if __name__ == "__main__":
    main()
