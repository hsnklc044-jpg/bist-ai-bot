import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from institutional_engine import generate_weekly_report


TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏦 BIST CORE MODEL AKTİF\n\n"
        "Komutlar:\n"
        "/status\n"
        "/weekly"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Sistem aktif.\n"
        "📊 Haftalık Core rapor hazır."
    )


async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("📊 Haftalık Core rapor hazırlanıyor...")

    try:
        filename = generate_weekly_report()

        with open(filename, "rb") as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f
            )

        await update.message.reply_text("✅ Rapor gönderildi.")

    except Exception as e:
        await update.message.reply_text(f"❌ Hata:\n{e}")


def main():

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("weekly", weekly))

    print("BOT BAŞLADI")

    application.run_polling()


if __name__ == "__main__":
    main()
