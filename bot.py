import requests
import time
import os

from engine.ultimate_scanner import run_ultimate_scan
from engine.support_resistance_engine import get_support_resistance


TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


# ---------------------------------------------------
# TELEGRAM MESAJ GÖNDER
# ---------------------------------------------------

def send_message(text):

    url = f"{BASE_URL}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }

    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram mesaj hatası:", e)


# scheduler uyumluluğu için alias
def send_telegram_message(text):
    send_message(text)


# ---------------------------------------------------
# RADAR KOMUTU
# ---------------------------------------------------

def radar_command():

    print("📡 Radar taraması başlatıldı")

    signals = run_ultimate_scan()

    if not signals:
        return "Sinyal bulunamadı."

    message = "🚨 BIST AI RADAR SİNYALLERİ\n\n"

    for s in signals:

        message += f"""
📊 {s['symbol']}

💰 Fiyat: {s['price']}
📈 AI Skor: {s['score']}
🎯 Sinyal: {s['signal']}

"""

    return message


# ---------------------------------------------------
# DESTEK / DİRENÇ KOMUTU
# ---------------------------------------------------

def support_command(symbol):

    data = get_support_resistance(symbol)

    if not data:
        return "Veri bulunamadı."

    message = f"""
📊 {data['hisse']}

💰 Güncel Fiyat: {data['fiyat']}

🟢 Destek: {data['destek']}
🔴 Direnç: {data['direnc']}
"""

    return message


# ---------------------------------------------------
# TELEGRAM KOMUTLARINI DİNLE
# ---------------------------------------------------

def listen_commands():

    print("📡 Telegram komutları dinleniyor...")

    last_update = None

    while True:

        try:

            url = f"{BASE_URL}/getUpdates"

            params = {
                "timeout": 100,
                "offset": last_update
            }

            response = requests.get(url, params=params).json()

            if "result" not in response:
                time.sleep(2)
                continue

            updates = response["result"]

            for update in updates:

                last_update = update["update_id"] + 1

                if "message" not in update:
                    continue

                message = update["message"]

                text = message.get("text", "")

                print("Komut:", text)

                # RADAR
                if text.startswith("/radar"):

                    result = radar_command()

                    send_message(result)

                # SUPPORT
                elif text.startswith("/support"):

                    parts = text.split()

                    if len(parts) < 2:

                        send_message("Kullanım:\n/support THYAO")

                    else:

                        symbol = parts[1].upper()

                        result = support_command(symbol)

                        send_message(result)

        except Exception as e:

            print("Komut dinleme hatası:", e)

        time.sleep(2)


# ---------------------------------------------------
# BOT BAŞLAT
# ---------------------------------------------------

if __name__ == "__main__":

    print("🤖 BIST AI BOT BAŞLADI")

    listen_commands()
