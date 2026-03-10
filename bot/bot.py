import logging
from telegram.ext import Updater, CommandHandler

from radar_engine import radar_scan
from supabase_engine import save_signal
from trade_engine import open_trade
from price_engine import get_price

TOKEN = "8772282578:AAHayduiZtDuf659L0Fx9H8ehOcn81tii10"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def start(update, context):
    update.message.reply_text("BIST AI Bot hazır 🚀")


def radar(update, context):

    results = radar_scan()

    if not results:
        update.message.reply_text("Radar sinyali bulunamadı.")
        return

    message = "🔥 BIST AI Radar\n\n"

    for i, r in enumerate(results, start=1):

        symbol = r["symbol"]
        score = r["score"]

        # Gerçek fiyatı çek
        price = get_price(symbol)

        message += f"{i}️⃣ {symbol} ⭐ {score} | {price}₺\n"

        # Supabase signals kaydı
        save_signal(symbol, "RADAR", score, price)

        # Trade aç
        open_trade(symbol, "RADAR", price)

    update.message.reply_text(message)


def main():

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("radar", radar))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()