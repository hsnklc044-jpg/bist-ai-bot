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
    level=logging.INFO,
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

        symbol = args[0].upper()
        direction = args[1].lower()
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

        if not curve or len(curve) < 2:
            await update.message.reply_text("Henüz yeterli trade yok.")
            return

        final_equity = round(curve[-1], 3)

        await update.message.reply_text(
            f"📈 Güncel Equity: {final_equity}"
        )

    except Exception as e:
        logger.error(f"Equity error: {e}")
        await update.message.reply_text("❌ Equity hesaplanamadı.")

# =========================
# MAIN
# =========================

def main():
    # 🔥 TABLOYU OLUŞTUR
    init_db()

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addtrade", addtrade))
    application.add_handler(CommandHandler("equity", equity))

    application.run_polling()

# =========================

if __name__ == "__main__":
    main()
