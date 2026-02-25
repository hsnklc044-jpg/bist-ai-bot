import os
import logging
from datetime import datetime, time

from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from institutional_engine import (
    calculate_scores,
    calculate_weights,
    create_excel_report,
    index_trend_ok
)

# =============================
# ENV
# =============================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

logging.basicConfig(level=logging.INFO)

# =============================
# TELEGRAM KOMUTLARI
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏦 BIST INSTITUTIONAL MODEL 12.5 AKTİF\n\n"
        "Komutlar:\n"
        "/weekly → Haftalık Core Rapor\n"
        "/status → Sistem Durumu"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Sistem aktif.\n"
        "📊 Haftalık hibrit model hazır.\n"
        "🧠 Core + Tactical mimari çalışıyor."
    )

# =============================
# HAFTALIK RAPOR
# =============================

async def weekly_report(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("📊 Haftalık analiz başlatıldı...")

    if not index_trend_ok():
        await update.message.reply_text(
            "⚠️ Endeks zayıf (EMA50 < EMA200).\n"
            "Core risk azaltılması önerilir."
        )
        return

    try:
        df_top = calculate_scores()

        if df_top.empty:
            await update.message.reply_text("Veri alınamadı.")
            return

        df_weighted = calculate_weights(df_top)

        file_path = create_excel_report(df_weighted)

        await update.message.reply_text("📈 Core 5 hesaplandı.\nExcel oluşturuluyor...")

        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=InputFile(file_path)
        )

        await update.message.reply_text("✅ Haftalık rapor gönderildi.")

    except Exception as e:
        logging.error(str(e))
        await update.message.reply_text(f"Hata oluştu: {str(e)}")

# =============================
# OTOMATİK PAZARTESİ RAPORU
# =============================

async def scheduled_weekly(context: ContextTypes.DEFAULT_TYPE):

    if not CHAT_ID:
        return

    if not index_trend_ok():
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text="⚠️ Endeks zayıf. Core risk azaltılmalı."
        )
        return

    df_top = calculate_scores()
    df_weighted = calculate_weights(df_top)
    file_path = create_excel_report(df_weighted)

    await context.bot.send_message(
        chat_id=CHAT_ID,
        text="📊 Otomatik Haftalık Core Rapor"
    )

    await context.bot.send_document(
        chat_id=CHAT_ID,
        document=InputFile(file_path)
    )

# =============================
# MAIN
# =============================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("weekly", weekly_report))

    # Her Pazartesi 09:00 otomatik rapor
    app.job_queue.run_daily(
        scheduled_weekly,
        time=time(hour=9, minute=0),
        days=(0,)  # Pazartesi
    )

    app.run_polling()

if __name__ == "__main__":
    main()
