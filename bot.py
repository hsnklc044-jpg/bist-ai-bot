# bot.py

import os
import logging
import sqlite3
import matplotlib.pyplot as plt

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

DB_NAME = "trades.db"

# --------------------------------------------------
# LOGGING
# --------------------------------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

# --------------------------------------------------
# EQUITY CURVE FUNCTION
# --------------------------------------------------

def get_equity_curve():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT r_multiple FROM trades")
    rows = c.fetchall()
    conn.close()

    trades = [r[0] for r in rows]

    equity = 1.0
    curve = [equity]

    for r in trades:
        equity *= (1 + r * 0.01)
        curve.append(equity)

    return curve

# --------------------------------------------------
# COMMANDS
# --------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 BIST AI Quant Bot Aktif\n\n"
        "Komutlar:\n"
        "/dashboard\n"
        "/multiplier\n"
        "/addtrade SYMBOL long/short entry exit risk%\n"
        "/equity"
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


async def equity_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        curve = get_equity_curve()

        if len(curve) <= 1:
            await update.message.reply_text("Henüz yeterli trade yok.")
            return

        plt.figure()
        plt.plot(curve)
        plt.title("Equity Curve")
        plt.xlabel("Trade Number")
        plt.ylabel("Equity Growth")

        file_path = "equity.png"
        plt.savefig(file_path)
        plt.close()

        await update.message.reply_photo(photo=open(file_path, "rb"))

    except Exception:
        logger.exception("Equity error")
        await update.message.reply_text("❌ Equity grafiği üretilemedi.")


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

    init_db()

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dashboard", dashboard))
    app.add_handler(CommandHandler("multiplier", multiplier_command))
    app.add_handler(CommandHandler("addtrade", add_trade_command))
    app.add_handler(CommandHandler("equity", equity_command))

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
