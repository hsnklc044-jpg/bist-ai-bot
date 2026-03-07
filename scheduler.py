import requests
import os
from scanner import scan_market

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=payload)


def run():

    signals = scan_market()

    message = "🚀 BIST AI RADAR\n\n"

    for s in signals:

        message += f"""
{s['ticker']}
RSI: {s['rsi']}
Volume Spike: {s['volume_spike']}
AI Score: {s['score']}
-------------------
"""

    send(message)


if __name__ == "__main__":
    run()
