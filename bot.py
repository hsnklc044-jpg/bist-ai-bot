import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from performance_tracker import get_performance_report
from risk_engine import log_trade

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# =========================
# COMMANDS
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Institutional Portfolio Engine v2 aktif."
    )


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        report_data = get_performance_report()

        message = (
            "📊 PERFORMANS RAPORU\n\n"
            f"Toplam İşlem: {report_data['total_trades']}\n"
            f"Kazanan: {report_data['wins']}\n"
            f"Kaybeden: {report_data['losses']}\n"
            f"Net Kar: {report_data['net_profit']} TL\n"
            f"Güncel Equity: {report_data['equity']} TL"
        )

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"❌ Hata oluştu:\n{str(e)}")


async def testtrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        profit = log_trade(
            symbol="BIST30",
            side="long",
            entry_price=100,
            exit_price=110,
            quantity=10
        )

        await update.message.reply_text(
            f"✅ Test trade eklendi.\nKar: {profit} TL"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Trade eklenemedi:\n{str(e)}")


# =========================
# MAIN
# =========================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("testtrade", testtrade))

    logger.info("Institutional Portfolio Engine v2 başlatıldı...")

    app.run_polling()


if __name__ == "__main__":
    main()
