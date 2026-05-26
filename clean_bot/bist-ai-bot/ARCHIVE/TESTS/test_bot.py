from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8723764154:AAHkeF12Ci70As-dTRamEDnzUbXUlAcLLLY"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("CALISIYOR")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("TEST BOT CALISIYOR")
    app.run_polling()

if __name__ == "__main__":
    main()
