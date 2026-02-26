import os
import logging
from datetime import time

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from institutional_engine import generate_weekly_report


TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # kendi chat id'n


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


# =============================
# MANUEL KOMUTLAR
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏦 BIST Core Engine Aktif")


async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_report(context, update.effective_chat.id)


# =============================
# OTOMATİK RAPOR
# =============================

async def auto_morning_report(context: ContextTypes.DEFAULT_TYPE):
    await send_report(context, CHAT_ID)


async def send_report(context, chat_id):

    try:
        filename, summary = generate_weekly_report()

        await context.bot.send_message(
            chat_id=chat_id,
            text="📊 Sabah Otomatik Core Raporu"
        )

        if os.path.exists(filename):
            with open(filename, "rb") as f:
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=f
                )

        await context.bot.send_message(
            chat_id=chat_id,
            text=summary
        )

    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ Sabah rapor hatası:\n{str(e)}"
        )


# =============================
# MAIN
# =============================

def main():

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("weekly", weekly))

    # ⏰ HER GÜN 09:15
    application.job_queue.run_daily(
        auto_morning_report,
        time=time(9, 15)
    )

    print("🚀 Core Engine + Sabah Scheduler Aktif")

    application.run_polling()


if __name__ == "__main__":
    main()
