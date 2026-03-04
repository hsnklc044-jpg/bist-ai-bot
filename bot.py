# bot.py

from telegram import Bot
from config import TELEGRAM_TOKEN, CHAT_ID, BIST_SYMBOLS
from data_service import get_data
from indicators import add_indicators
from app.scoring_engine import score_stock
from filters import classify
from market_filter import market_is_positive
from report_formatter import format_report

def morning_scan():

    if not market_is_positive():
        return "Piyasa zayıf. Sinyal üretilmedi."

    results = []

    for symbol in BIST_SYMBOLS:
        df = get_data(symbol)
        df = add_indicators(df)

        score = calculate_score(df)
        category = classify(score)

        if category:
            results.append((symbol, score, category))

    results = sorted(results, key=lambda x: x[1], reverse=True)[:5]

    return format_report(results)


def send_morning_report():
    bot = Bot(token=TELEGRAM_TOKEN)
    message = morning_scan()
    bot.send_message(chat_id=CHAT_ID, text=message)


if __name__ == "__main__":
    send_morning_report()
