import json
import requests
from logger_engine import log_info

TOKEN = "8772282578:AAHayduiZtDuf659L0Fx9H8ehOcn81tii10"
CHAT_ID = "1790584407"


def send_message(text):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    requests.post(url,data=data)


def run_telegram_signals():

    try:
        with open("ultra_signals.json","r") as f:
            signals = json.load(f)

    except:
        log_info("Ultra signals missing")
        return


    for s in signals:

        message = f"""
🔥 ULTRA AI SIGNAL

{s['symbol']}

Score: {s['score']}
Momentum: {s['momentum']}
Price: {s['price']}
RSI: {s['rsi']}

🎯 Target: {s['target']}
🛑 Stop: {s['stop']}
📊 Risk: {s['risk']}%
"""

        send_message(message)

        log_info(f"Ultra signal sent {s['symbol']}")


if __name__ == "__main__":
    run_telegram_signals()
