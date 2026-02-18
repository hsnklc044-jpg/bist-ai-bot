import os
import time
import requests

TOKEN = os.environ.get("TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"

offset = None

print("BOT BASLADI")

while True:
    try:
        r = requests.get(f"{URL}/getUpdates", params={"offset": offset, "timeout": 30})
        data = r.json()

        if not data.get("ok"):
            print("Telegram hata:", data)
            time.sleep(5)
            continue

        for update in data.get("result", []):
            offset = update["update_id"] + 1

            if "message" in update:
                chat_id = update["message"]["chat"]["id"]
                text = update["message"].get("text", "")

                if text.lower() == "/start":
                    msg = "🤖 BIST AI aktif.\nSistem çalışıyor."
                else:
                    msg = f"Komut alındı: {text}"

                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": msg})

        time.sleep(1)

    except Exception as e:
        print("HATA:", e)
        time.sleep(5)
