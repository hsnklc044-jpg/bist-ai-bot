import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from institutional_engine import generate_weekly_report


TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏦 Institutional BIST Engine Aktif")


async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("📊 Rapor hazırlanıyor...")

    try:
        filename, telegram_text = generate_weekly_report()

        if os.path.exists(filename):
            with open(filename, "rb") as f:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=f,
                    filename="bist_core_report.xlsx"
                )

        await update.message.reply_text(telegram_text)

    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)}")


def main():

    if not TOKEN:
        raise ValueError("BOT_TOKEN eksik!")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weekly", weekly))

    print("🚀 PROFESSIONAL ENGINE AKTİF")

    app.run_polling()


if __name__ == "__main__":
    main()
