import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from institutional_engine import generate_weekly_report

TOKEN = os.getenv("BOT_TOKEN")

equity = 100000
wins = 0
losses = 0
trades = 0
peak_equity = equity


# =========================
# STATUS
# =========================
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global equity, wins, losses, trades, peak_equity

    winrate = (wins / trades * 100) if trades > 0 else 0
    drawdown = ((peak_equity - equity) / peak_equity * 100) if peak_equity > 0 else 0

    text = (
        f"💰 Bakiye: {equity:.2f}\n"
        f"📊 Kazanma Oranı: {winrate:.2f}%\n"
        f"📉 Drawdown: {drawdown:.2f}%\n"
        f"🔁 İşlem Sayısı: {trades}"
    )

    await update.message.reply_text(text)


# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 HEDGE FUND MODE 7.0 AKTİF\n"
        "Gerçek SL/TP Takibi\n"
        "Günlük Risk Limiti %3"
    )


# =========================
# WEEKLY REPORT
# =========================
async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Haftalık Kurumsal Rapor hazırlanıyor...")

    try:
        filename = generate_weekly_report()

        with open(filename, "rb") as file:
            await update.message.reply_document(document=file)

    except Exception as e:
        await update.message.reply_text(f"❌ Hata oluştu:\n{e}")


# =========================
# MAIN
# =========================
async def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("weekly", weekly))

    print("BOT BAŞLADI")
    await application.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
