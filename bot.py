import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from trade_engine import init_db, add_trade, get_equity_curve


# =========================
# ENV VARIABLES
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# =========================
# LOGGING
# =========================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# =========================
# COMMAND: /start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("BIST AI Bot aktif 🚀")


# =========================
# COMMAND: /addtrade
# Örnek:
# /addtrade EREGL long 45 47
# =========================
async def addtrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args

        if len(args) != 4:
            await update.message.reply_text(
                "Kullanım:\n/addtrade SYMBOL long/short entry exit"
            )
            return

        symbol = args[0]
        direction = args[1]
        entry = float(args[2])
        exit_price = float(args[3])

        add_trade(symbol, direction, entry, exit_price)

        await update.message.reply_text(
            f"✅ Trade kaydedildi:\n"
            f"{symbol} {direction}\n"
            f"Entry: {entry}\n"
            f"Exit: {exit_price}"
        )

    except Exception as e:
        logger.error(f"Addtrade error: {e}")
        await update.message.reply_text("❌ Trade kaydedilemedi.")


# =========================
# COMMAND: /equity
# =========================
async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        curve = get_equity_curve()

        if len(curve) <= 1:
            await update.message.reply_text("Henüz yeterli trade yok.")
            return

        final_equity = round(curve[-1], 4)

        await update.message.reply_text(
            f"📈 Equity Curve\n\n"
            f"Toplam Trade: {len(curve) - 1}\n"
            f"Final Equity: {final_equity}"
        )

    except Exception as e:
        logger.error(f"Equity error: {e}")
        await update.message.reply_text("❌ Equity hesaplanamadı.")


# =========================
# MAIN
# =========================
def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN environment variable not set")

    init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addtrade", addtrade))
    app.add_handler(CommandHandler("equity", equity))

    logger.info("Bot başlatıldı...")
    app.run_polling()


if __name__ == "__main__":
    main()
