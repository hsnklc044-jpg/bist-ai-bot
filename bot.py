import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from performance_tracker import (
    get_position_multiplier,
    get_bayesian_winrate,
    get_avg_rr,
    calculate_drawdown,
    get_loss_streak,
    get_volatility_regime,
    monte_carlo_tail_risk,
)

TOKEN = os.getenv("TELEGRAM_TOKEN")


async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    multiplier = get_position_multiplier()
    winrate = get_bayesian_winrate()
    rr = get_avg_rr()
    dd = calculate_drawdown()
    streak = get_loss_streak()
    regime = get_volatility_regime()
    mc = monte_carlo_tail_risk()

    await update.message.reply_text(
        "📊 QUANT CORE DASHBOARD\n\n"
        f"Bayesian Win Rate: {round(winrate*100,2)}%\n"
        f"Avg R:R: {round(rr,2)}\n"
        f"Monte Carlo Tail Ratio: {round(mc,2)}\n"
        f"Drawdown: {round(dd,2)}%\n"
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
