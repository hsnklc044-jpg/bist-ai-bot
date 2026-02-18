import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from ai_signal_engine import run_daily_scan   # ✅ BURAYA

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("BIST AI aktif. Sistem çalışıyor.")


async def rapor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Günlük tarama hazırlanıyor...")
    run_daily_scan()


def main():
    print("TOKEN:", TOKEN)
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rapor", rapor))

    print("Bot çalıştı...")
    app.run_polling()


if __name__ == "__main__":
    main()
