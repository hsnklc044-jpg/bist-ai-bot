import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("BIST AI aktif. Sistem çalışıyor.")


async def rapor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Günlük tarama başlatıldı...")

    try:
        from ai_signal_engine import run_daily_scan
        sonuc = run_daily_scan()
        await update.message.reply_text(f"SONUÇ:\n{sonuc}")
    except Exception as e:
        await update.message.reply_text(f"HATA:\n{e}")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rapor", rapor))  # ⭐ EN KRİTİK SATIR

    print("Bot çalıştı...")
    app.run_polling()


if __name__ == "__main__":
    main()
