# bot.py

import os
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from performance_tracker import (
    get_position_multiplier,
    get_bayesian_winrate,
    get_avg_rr,
    calculate_drawdown,
    get_loss_streak,
    get_volatility_regime,
    monte_carlo_tail_risk,
    detect_regime_change,
)

# --------------------------------------------------
# LOGGING
# --------------------------------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

# --------------------------------------------------
# COMMANDS
# --------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 BIST AI Bot aktif.\n\n"
        "Komutlar:\n"
        "/dashboard\n"
        "/multiplier"
    )


async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        multiplier = get_position_multiplier()
        winrate = get_bayesian_winrate()
        rr = get_avg_rr()
        dd = calculate_drawdown()
        streak = get_loss_streak()
        vol_regime = get_volatility_regime()
        mc = monte_carlo_tail_risk()
        regime_shift = detect_regime_change()

        message = (
            "📊 QUANT CORE DASHBOARD\n\n"
            f"Bayesian Win Rate: {round(winrate * 100, 2)}%\n"
            f"Avg R:R: {round(rr, 2)}\n"
            f"Monte Carlo Tail Ratio: {round(mc, 2)}\n"
            f"Drawdown: {round(dd, 2)}%\n"
            f"Loss Streak: {streak}\n"
            f"Volatility Regime: {vol_regime}\n"
            f"Regime Shift: {regime_shift}\n\n"
            f"Final Position Multiplier: {multiplier}"
        )

        await update.message.reply_text(message)

    except Exception as e:
        logger.exception("Dashboard error")
        await update.message.reply_text("❌ Dashboard hesaplanamadı.")


async def multiplier_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m = get_position_multiplier()
        await update.message.reply_text(
            f"📈 Current Position Multiplier: {m}"
        )
    except Exception:
        logger.exception("Multiplier error")
        await update.message.reply_text("❌ Multiplier hesaplanamadı.")


# --------------------------------------------------
# ERROR HANDLER
# --------------------------------------------------

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling update:", exc_info=context.error)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    token = os.getenv("TELEGRAM_TOKEN")

    if not token:
        raise ValueError("TELEGRAM_TOKEN environment variable not set.")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dashboard", dashboard))
    app.add_handler(CommandHandler("multiplier", multiplier_command))

    app.add_error_handler(error_handler)

    logger.info("Bot başlatıldı...")

    app.run_polling(
        poll_interval=3,
        timeout=30,
        drop_pending_updates=True,
        close_loop=False,
    )


if __name__ == "__main__":
    main()
