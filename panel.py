import os
import time
import requests

TOKEN = os.environ.get("8500392750:AAHprLseYkYGlF6zTw8YJ4doFLqwwvOSjVM")
URL = f"https://api.telegram.org/bot{TOKEN}"

offset = None

print("BOT BAŞLADI")

while True:
    try:
        r = requests.get(f"{URL}/getUpdates", params={"offset": offset, "timeout": 30})
        data = r.json()

        for update in data["result"]:
            offset = update["update_id"] + 1

            if "message" in update:
                chat_id = update["message"]["chat"]["id"]
                text = update["message"].get("text", "")

                if text == "/start":
                    msg = "🤖 BIST AI aktif.\nSistem çalışıyor."
                else:
                    msg = f"Komut: {text}"

                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": msg})

    except Exception as e:
        print("HATA:", e)
        time.sleep(5)
