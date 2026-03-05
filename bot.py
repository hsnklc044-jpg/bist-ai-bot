import requests
import time
import threading
import os

from engine.ultimate_scanner import run_ultimate_scan
from engine.support_resistance_engine import calculate_support_resistance


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# TELEGRAM MESAJ GÖNDER
def send_telegram_message(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=payload)


# RADAR MESAJ FORMATLAMA
def format_radar(signals):

    if not signals:
        return "⚠️ Güçlü sinyal bulunamadı."

    message = "🚨 BIST AI RADAR\n\n"

    for s in signals:

        message += f"📊 {s['symbol']}\n"
        message += f"💰 Fiyat: {s['price']}\n"
        message += f"📈 AI Skor: {s['score']}\n"
        message += f"🎯 {s['signal']}\n\n"

    return message


# TELEGRAM KOMUTLARI
def listen_commands():

    print("📡 Telegram komutları dinleniyor...")

    offset = None

    while True:

        try:

            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

            params = {"timeout": 100, "offset": offset}

            res = requests.get(url, params=params).json()

            if "result" not in res:
                time.sleep(2)
                continue

            for update in res["result"]:

                offset = update["update_id"] + 1

                if "message" not in update:
                    continue

                text = update["message"].get("text", "")

                # RADAR
                if text == "/radar":

                    signals = run_ultimate_scan()

                    msg = format_radar(signals)

                    send_telegram_message(msg)

                # SUPPORT
                if text.startswith("/support"):

                    parts = text.split()

                    if len(parts) < 2:
                        send_telegram_message("⚠️ Hisse yazmalısın.\nÖrnek: /support THYAO")
                        continue

                    symbol = parts[1].upper()

                    result = calculate_support_resistance(symbol)

                    if result is None:

                        send_telegram_message("Veri bulunamadı.")

                        continue

                    price = result["price"]
                    support = result["support"]
                    resistance = result["resistance"]

                    message = f"""
📊 {symbol}

💰 Fiyat: {price}

🟢 Destek: {support}

🔴 Direnç: {resistance}
"""

                    send_telegram_message(message)

        except Exception as e:

            print("Komut hatası:", e)

            time.sleep(5)


# RENDER PORT SERVER (ÜCRETSİZ ÇALIŞMASI İÇİN)
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"BIST AI BOT RUNNING")


def run_server():

    port = int(os.environ.get("PORT", 10000))

    server = HTTPServer(("0.0.0.0", port), Handler)

    server.serve_forever()


# BOT BAŞLAT
def start_bot():

    print("🤖 BIST AI BOT BAŞLADI")

    threading.Thread(target=listen_commands).start()

    run_server()


if __name__ == "__main__":

    start_bot()
