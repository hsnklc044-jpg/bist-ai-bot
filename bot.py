import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from performance_tracker import (
    get_position_multiplier,
    calculate_drawdown,
    get_loss_streak,
    get_volatility_regime,
    get_bayesian_winrate,
    get_avg_rr,
)

TOKEN = os.getenv("TELEGRAM_TOKEN")


async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dd, dd_percent = calculate_drawdown()
    streak = get_loss_streak()
    regime = get_volatility_regime()
    multiplier = get_position_multiplier()
    winrate = get_bayesian_winrate()
    rr = get_avg_rr()

    await update.message.reply_text(
        "📊 QUANT RISK DASHBOARD\n\n"
        f"Bayesian Win Rate: {round(winrate*100,2)}%\n"
        f"Avg R:R: {round(rr,2)}\n"
        f"Drawdown: {dd_percent}%\n"
        f"Loss Streak: {streak}\n"
        f"Volatility Regime: {regime}\n\n"
        f"Final Position Multiplier: {multiplier}"
    )


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("dashboard", dashboard))
    app.run_polling()


if __name__ == "__main__":
    main()
