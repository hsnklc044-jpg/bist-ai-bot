import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from performance_tracker import (
    get_position_multiplier,
    calculate_drawdown,
    get_loss_streak,
    get_volatility_regime,
)

TOKEN = os.getenv("TELEGRAM_TOKEN")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dd, dd_percent = calculate_drawdown()
    streak = get_loss_streak()
    regime = get_volatility_regime()
    multiplier = get_position_multiplier()

    await update.message.reply_text(
        "📊 FULL RISK STATUS\n\n"
        f"Drawdown: {dd_percent}%\n"
        f"Loss Streak: {streak}\n"
        f"Volatility Regime: {regime}\n"
        f"Position Multiplier: {multiplier}"
    )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("status", status))

    app.run_polling()


if __name__ == "__main__":
    main()
