import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from performance_tracker import (
    check_consecutive_losses,
    get_position_multiplier,
)

TOKEN = os.getenv("TELEGRAM_TOKEN")


async def lossstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status, streak = check_consecutive_losses()

    message = (
        "📉 LOSS STREAK STATUS\n\n"
        f"Current Streak: {streak}\n"
        f"Status: {status}"
    )

    await update.message.reply_text(message)


async def position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    multiplier = get_position_multiplier()

    await update.message.reply_text(
        f"📏 POSITION MULTIPLIER\n\nMultiplier: {multiplier}x"
    )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("lossstatus", lossstatus))
    app.add_handler(CommandHandler("position", position))

    app.run_polling()


if __name__ == "__main__":
    main()
