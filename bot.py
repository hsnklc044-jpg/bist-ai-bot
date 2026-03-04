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
        return "📉 Piyasa zayıf. Sinyal üretilmedi."

    results = []

    for symbol in BIST_SYMBOLS:

        try:

            df = get_data(symbol)

            if df is None or df.empty:
                continue

            df = add_indicators(df)

            score = score_stock(df)

            category = classify(score)

            if category:
                results.append((symbol, score, category))

        except Exception as e:

            print(f"Hata oluştu: {symbol} -> {e}")

    results = sorted(results, key=lambda x: x[1], reverse=True)[:5]

    return format_report(results)


def send_to_telegram(message):

    bot = Bot(token=TELEGRAM_TOKEN)

    bot.send_message(chat_id=CHAT_ID, text=message)


def main():

    print("📡 Sabah radar taraması başlıyor...")

    report = morning_scan()

    print(report)

    send_to_telegram(report)

    print("✅ Telegram mesajı gönderildi.")


if __name__ == "__main__":
    main()
