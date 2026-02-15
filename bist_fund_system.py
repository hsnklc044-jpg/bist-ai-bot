import os
import requests
import traceback

TELEGRAM_TOKEN = os.getenv("8440357756:AAGdYajs2PirEhY2O9R8Voe_JmtAQhIHI8I")
TELEGRAM_CHAT_ID = os.getenv("1790584407")


def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})


def main():
    try:
        # --- BURASI GERÇEK AI KODU YERİ ---
        # Şimdilik test:
        mesaj = "🚀 AI motoru çalıştı. Buraya portföy gelecek."

        send_telegram(mesaj)

    except Exception as e:
        hata = "❌ HATA:\n\n" + str(e) + "\n\n" + traceback.format_exc()
        send_telegram(hata)


if __name__ == "__main__":
    main()
