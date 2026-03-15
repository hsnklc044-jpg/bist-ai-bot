import requests
from logger_engine import log_info, log_error

TOKEN = "8772282578:AAHayduiZtDuf659L0Fx9H8ehOcn81tii10"
CHAT_ID = "1790584407"


def send_telegram(message):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:

        requests.post(url, data=payload)

        log_info("Telegram message sent")

    except Exception as e:

        log_error(f"Telegram error: {e}")


def send_chart(symbol):

    filename = f"{symbol}.png"

    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    try:

        files = {"photo": open(filename, "rb")}

        data = {"chat_id": CHAT_ID}

        requests.post(url, files=files, data=data)

        log_info(f"Chart sent for {symbol}")

    except Exception as e:

        log_error(f"Chart send error: {e}")


def send_portfolio(portfolio):

    if not portfolio:
        return

    message = "📊 BUGÜNÜN PORTFÖYÜ\n\n"

    for symbol, weight in portfolio:

        message += f"{symbol} → %{weight}\n"

    send_telegram(message)
