import requests

class TelegramNotifier:

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    def send(self, message):

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        data = {
            "chat_id": self.chat_id,
            "text": message
        }

        try:

            requests.post(
                url,
                data=data,
                timeout=10
            )

            print("[TELEGRAM] Message sent")

        except Exception as e:

            print(f"[TELEGRAM ERROR] {e}")