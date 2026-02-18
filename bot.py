import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
print("TOKEN:", TOKEN)
print("CHAT_ID:", CHAT_ID)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("BIST AI aktif. Sistem çalışıyor.")


def main():
    print("TOKEN:", TOKEN)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    print("Bot çalıştı...")
    app.run_polling()


if __name__ == "__main__":
    main()
