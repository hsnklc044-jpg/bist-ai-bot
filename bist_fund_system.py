import os
import requests

print("TOKEN =", os.getenv("8440357756:AAGdYajs2PirEhY2O9R8Voe_JmtAQhIHI8I"))
print("CHAT_ID =", os.getenv("1790584407"))

url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage"

payload = {
    "chat_id": os.getenv("TELEGRAM_CHAT_ID"),
    "text": "TEST MESAJI — GITHUB"
}

r = requests.post(url, data=payload)
print("TELEGRAM CEVAP:", r.text)
