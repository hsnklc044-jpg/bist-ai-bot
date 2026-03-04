import time
import schedule
import datetime
import threading
import os

from engine.ultimate_scanner import run_ultimate_scan
from bot import send_telegram_message, listen_commands


def market_is_open():

    now = datetime.datetime.now()

    # hafta sonu çalışmasın
    if now.weekday() >= 5:
        return False

    start = now.replace(hour=10, minute=0, second=0)
    end = now.replace(hour=18, minute=0, second=0)

    return start <= now <= end


def radar_job():

    if not market_is_open():
        print("Piyasa kapalı, radar çalışmadı.")
        return

    print("📡 Radar taraması başladı")

    try:

        signals = run_ultimate_scan()

        for signal in signals:
            send_telegram_message(signal)

    except Exception as e:

        print("Radar hatası:", e)

    print("✅ Radar tamamlandı")


# 15 dakikada bir radar
schedule.every(15).minutes.do(radar_job)


# Telegram komut dinleyici
command_thread = threading.Thread(target=listen_commands)
command_thread.daemon = True
command_thread.start()


print("🚀 BIST AI Radar başlatıldı")


# -------- Render için PORT açma --------

from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 10000))


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"BIST AI BOT running")


def run_server():

    server = HTTPServer(("0.0.0.0", PORT), Handler)

    print(f"🌐 Web server started on port {PORT}")

    server.serve_forever()


# web server ayrı thread
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()


# scheduler loop
while True:

    schedule.run_pending()

    time.sleep(10)
