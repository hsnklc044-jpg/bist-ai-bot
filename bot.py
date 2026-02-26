import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from institutional_engine import generate_weekly_report, save_balance


TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏦 Risk Motoru Aktif")


async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("📊 Rapor hazırlanıyor...")

    filename, text = generate_weekly_report()

    with open(filename, "rb") as f:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=f)

    await update.message.reply_text(text)


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Kullanım: /balance 150000")
        return

    try:
        amount = int(context.args[0])
        save_balance(amount)
        await update.message.reply_text(f"✅ Yeni portföy: {amount} TL")
    except:
        await update.message.reply_text("Geçersiz değer.")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weekly", weekly))
    app.add_handler(CommandHandler("balance", balance))

    app.run_polling()


if __name__ == "__main__":
    main()
