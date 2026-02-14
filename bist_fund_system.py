import os
import requests


# ==============================
# GitHub Secrets'ten alınır
# ==============================
TELEGRAM_TOKEN = os.getenv("8440357756:AAHjY_XiqJv36QRDZmIk0P3-9I-9A1Qbg68")
TELEGRAM_CHAT_ID = os.getenv("1790584407")


# ==============================
# Telegram mesaj gönderme
# ==============================
def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram bilgileri eksik.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        print("📨 Telegram cevap:", response.text)
    except Exception as e:
        print("❌ Telegram gönderim hatası:", e)


# ==============================
# Ana çalışma fonksiyonu
# ==============================
def main():
    print("🚀 BIST AI BOT başlatıldı...")

    message = """
✅ <b>BIST AI BOT AKTİF</b>

Telegram bağlantısı başarıyla kuruldu.
GitHub Actions sorunsuz çalışıyor.

Artık sinyal sistemi entegre edilebilir.
"""

    print(message)
    send_telegram(message)


# ==============================
# Çalıştır
# ==============================
if __name__ == "__main__":
    main()
