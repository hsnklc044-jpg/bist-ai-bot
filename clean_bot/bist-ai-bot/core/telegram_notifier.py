import requests

BOT_TOKEN = "8434925197:AAHeciNObLAkLJ_SE_jsaNPvhiwR9_HRoTE"
CHAT_ID = "1790584407"


def send_ai_signal(data):

    message = f"""
🤖 AI FILTER SIGNAL

Symbol: {data['symbol']}

Signal: {data['signal']}

AI Score: {data['score']}

Trend: {data['trend']}

RSI: {data['rsi']}

MACD: {data['macd']}

Volatility: {data['volatility']}

Volume Ratio: {data['volume_ratio']}
"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:

        requests.post(url, data=payload)

        print("[TELEGRAM] AI Signal Sent")

    except Exception as e:

        print(f"[TELEGRAM ERROR] {e}")