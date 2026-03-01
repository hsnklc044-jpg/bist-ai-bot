import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

from performance_tracker import (
    get_performance_report,
    get_risk_metrics
)


# ==============================
# Logging
# ==============================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


TOKEN = os.getenv("TELEGRAM_TOKEN")


# ==============================
# Commands
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Institutional Portfolio Engine (Stable Core) aktif.\n\n"
        "Komutlar:\n"
        "/report\n"
        "/risk"
    )


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = get_performance_report()

        message = (
            "📊 PERFORMANS RAPORU\n\n"
            f"Toplam İşlem: {data['total_trades']}\n"
            f"Kazanan: {data['wins']}\n"
            f"Kaybeden: {data['losses']}\n"
            f"Net Kar: {data['net_profit']} TL\n"
            f"Güncel Equity: {data['equity']} TL"
        )

        await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Report error: {e}")
        await update.message.reply_text("❌ Report oluşturulamadı.")


async def risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = get_risk_metrics()

        message = (
            "📈 RISK METRICS PANEL\n\n"
            f"Win Rate: {data['win_rate']}%\n"
            f"Profit Factor: {data['profit_factor']}\n"
            f"Avg Win: {data['avg_win']} TL\n"
            f"Avg Loss: {data['avg_loss']} TL\n"
            f"Expectancy: {data['expectancy']} TL\n"
            f"Sharpe Ratio: {data['sharpe']}"
        )

        await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Risk error: {e}")
        await update.message.reply_text("❌ Risk hesaplanamadı.")


# ==============================
# Main
# ==============================

def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN environment variable not set.")

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("report", report))
    application.add_handler(CommandHandler("risk", risk))

    logger.info("Institutional Portfolio Engine Stable Core başlatıldı...")

    application.run_polling()


if __name__ == "__main__":
    main()
