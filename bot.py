import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from performance_tracker import (
    get_kelly_fraction,
    get_loss_streak,
    calculate_drawdown,
)

TOKEN = os.getenv("TELEGRAM_TOKEN")


async def kelly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fraction = get_kelly_fraction()

    await update.message.reply_text(
        f"🧠 ADAPTIVE KELLY\n\n"
        f"Recommended Risk Fraction: {fraction * 100}%"
    )


async def riskstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dd, dd_percent = calculate_drawdown()
    streak = get_loss_streak()

    await update.message.reply_text(
        f"📊 RISK STATUS\n\n"
        f"Drawdown: {dd_percent}%\n"
        f"Loss Streak: {streak}"
    )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("kelly", kelly))
    app.add_handler(CommandHandler("riskstatus", riskstatus))

    app.run_polling()


if __name__ == "__main__":
    main()
