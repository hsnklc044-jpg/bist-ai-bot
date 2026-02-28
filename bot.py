import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from performance_tracker import init_db, get_performance_summary

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Institutional Portfolio Engine v2 aktif.")


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        result = get_performance_summary()

        message = f"""
📊 PERFORMANS RAPORU

Toplam İşlem: {result['total_trades']}
Kazanan: {result['wins']}
Kaybeden: {result['losses']}
Net Kar: {round(result['net_profit'], 2)} TL
Güncel Equity: {round(result['equity'], 2)} TL
        """

        await update.message.reply_text(message)

    except Exception as e:
        logger.exception("Report error")
        await update.message.reply_text(f"❌ Hata oluştu:\n{str(e)}")


def main():
    init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", report))

    logger.info("Institutional Portfolio Engine v2 başlatıldı...")
    app.run_polling()


if __name__ == "__main__":
    main()
