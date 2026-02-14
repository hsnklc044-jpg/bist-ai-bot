import os
import requests

# GitHub Secrets'ten al
TELEGRAM_TOKEN = os.environ.get("8440357756:AAGdYajs2PirEhY2O9R8Voe_JmtAQhIHI8I")
TELEGRAM_CHAT_ID = os.environ.get("1790584407")


def send_telegram(message: str):
    """Telegram'a mesaj gönderir."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        r = requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
            },
            timeout=10,
        )

        print("Telegram cevap:", r.text)

    except Exception as e:
        print("Telegram gönderilemedi:", e)


def backtest():
    """Şimdilik test mesajı üret."""
    return ["TEST MESAJI — GITHUB"]


if __name__ == "__main__":
    print("AI Fon Yöneticisi çalışıyor...")

    signals = backtest()

    if not signals:
        text = "Bugün sinyal yok."
    else:
        text = "\n".join(signals)

    print("Gönderilecek mesaj:", text)

    send_telegram(text)
