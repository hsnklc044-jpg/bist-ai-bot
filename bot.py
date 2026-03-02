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
    get_avg_r,
    calculate_drawdown,
)

from trade_engine import init_db, log_trade

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
        "🤖 BIST AI Quant Bot Aktif\n\n"
        "Komutlar:\n"
        "/dashboard\n"
        "/multiplier\n"
        "/addtrade SYMBOL long/short entry exit risk%"
    )


async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        winrate = get_bayesian_winrate()
        avg_r = get_avg_r()
        drawdown = calculate_drawdown()
        multiplier = get_position_multiplier()

        message = (
            "📊 QUANT CORE DASHBOARD\n\n"
            f"Win Rate: {round(winrate * 100, 2)}%\n"
            f"Avg R: {round(avg_r, 2)}\n"
            f"Drawdown: {drawdown}%\n\n"
            f"Kelly Position Multiplier: {multiplier}"
        )

        await update.message.reply_text(message)

    except Exception:
        logger.exception("Dashboard error")
        await update.message.reply_text("❌ Dashboard hesaplanamadı.")


async def multiplier_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m = get_position_multiplier()
        await update.message.reply_text(
            f"📈 Current Kelly Multiplier: {m}"
        )
    except Exception:
        logger.exception("Multiplier error")
        await update.message.reply_text("❌ Multiplier hesaplanamadı.")


async def add_trade_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) != 5:
            await update.message.reply_text(
                "Kullanım:\n"
                "/addtrade SYMBOL long/short entry exit risk%"
            )
            return

        symbol = context.args[0]
        direction = context.args[1]
        entry = float(context.args[2])
        exit_price = float(context.args[3])
        risk_percent = float(context.args[4])

        log_trade(symbol, direction, entry, exit_price, risk_percent)

        await update.message.reply_text(
            f"✅ Trade kaydedildi:\n"
            f"{symbol} {direction}\n"
            f"Entry: {entry}\n"
            f"Exit: {exit_price}"
        )

    except Exception:
        logger.exception("Add trade error")
        await update.message.reply_text("❌ Trade eklenemedi.")


# --------------------------------------------------
# ERROR HANDLER
# --------------------------------------------------

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling update:", exc_info=context.error)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    token = os.getenv("TELEGRAM_TOKEN")

    if not token:
        raise ValueError("TELEGRAM_TOKEN environment variable not set.")

    # DB initialize
    init_db()

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dashboard", dashboard))
    app.add_handler(CommandHandler("multiplier", multiplier_command))
    app.add_handler(CommandHandler("addtrade", add_trade_command))

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
