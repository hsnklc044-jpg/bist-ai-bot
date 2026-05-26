import requests

# 🔴 BURAYA KENDİ BİLGİLERİNİ YAZ
BOT_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

def test_telegram():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": "🚀 TEST MESAJI BAŞARILI"
    }

    try:
        response = requests.post(url, data=payload, timeout=10)

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

    except Exception as e:
        print("HATA:", e)

if __name__ == "__main__":
    test_telegram()