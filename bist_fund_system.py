import requests

def main():
    token = "8440357756:AAGdYajs2PirEhY2O9R8Voe_JmtAQhIHI8I"
    chat_id = "1790584407"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": "🔥 GITHUB KESİN ÇALIŞTI"})

if __name__ == "__main__":
    main()
