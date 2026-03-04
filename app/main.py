import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

from radar_handler import radar

TOKEN = "BURAYA_BOT_TOKEN"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = (
        "📈 BIST AI BOT\n\n"
        "Komutlar:\n"
        "/radar  → Güçlü hisseleri tara\n"
    )

    await update.message.reply_text(message)


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("radar", radar))

    print("Bot çalışıyor...")

    app.run_polling()


if __name__ == "__main__":
    main()
