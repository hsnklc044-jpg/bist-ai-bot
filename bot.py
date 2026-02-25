import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from institutional_engine import generate_weekly_report


# =============================
# CONFIG
# =============================

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


# =============================
# COMMANDS
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏦 BIST HEDGE Fund Engine 20.0 AKTİF\n\n"
        "Komutlar:\n"
        "/status → Sistem durumu\n"
        "/weekly → Haftalık Core + Performans Raporu"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Sistem Çalışıyor\n"
        "📊 Core Engine Aktif\n"
        "📈 Equity Tracking Aktif\n"
        "🛡 Kill Switch Hazır"
    )


async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("📊 Haftalık Core rapor hazırlanıyor...")

    try:
        # ÖNEMLİ: tuple unpack
        filename, summary = generate_weekly_report()

        # Excel dosyası gönder
        if filename and os.path.exists(filename):

            with open(filename, "rb") as f:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=f,
                    filename="bist_core_report.xlsx"
                )

        # Performans özeti gönder
        if summary:
            await update.message.reply_text(summary)

        await update.message.reply_text("✅ Rapor tamamlandı.")

    except Exception as e:
        logging.error(str(e))
        await update.message.reply_text(f"❌ Hata:\n{str(e)}")


# =============================
# MAIN
# =============================

def main():

    if not TOKEN:
        raise ValueError("❌ BOT_TOKEN environment variable eksik!")

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("weekly", weekly))

    print("🚀 HEDGE FUND ENGINE 20.0 BAŞLADI")

    application.run_polling()


if __name__ == "__main__":
    main()
