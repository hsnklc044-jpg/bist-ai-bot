import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from institutional_engine import generate_weekly_report


TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

logging.basicConfig(level=logging.INFO)

LAST_REPORT_FILE = "last_report.txt"


# =============================
# GÜNLÜK RAPOR KONTROL
# =============================

async def check_daily_report(context):

    today = datetime.now().strftime("%Y-%m-%d")

    # Daha önce gönderilmiş mi?
    if os.path.exists(LAST_REPORT_FILE):
        with open(LAST_REPORT_FILE, "r") as f:
            last_date = f.read().strip()
        if last_date == today:
            return  # bugün zaten gönderilmiş

    # Gönder
    filename, summary = generate_weekly_report()

    await context.bot.send_message(
        chat_id=CHAT_ID,
        text="📊 Günlük BIST Öneri Raporu"
    )

    if os.path.exists(filename):
        with open(filename, "rb") as f:
            await context.bot.send_document(
                chat_id=CHAT_ID,
                document=f
            )

    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=summary
    )

    # Bugünün tarihini kaydet
    with open(LAST_REPORT_FILE, "w") as f:
        f.write(today)


# =============================
# KOMUTLAR
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_daily_report(context)
    await update.message.reply_text("🏦 Core Engine Aktif")


async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filename, summary = generate_weekly_report()

    if os.path.exists(filename):
        with open(filename, "rb") as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f
            )

    await update.message.reply_text(summary)


# =============================
# HER MESAJDA KONTROL
# =============================

async def any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_daily_report(context)


# =============================
# MAIN
# =============================

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weekly", weekly))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, any_message))

    print("🚀 Günlük Otomatik Rapor Sistemi Aktif")

    app.run_polling()


if __name__ == "__main__":
    main()
