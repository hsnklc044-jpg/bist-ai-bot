import os
import asyncio
from datetime import time

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from institutional_engine import (
    generate_weekly_report,
    save_balance,
    close_trade,
    get_equity_report,
)

TOKEN = os.getenv("BOT_TOKEN")


# ================= KOMUTLAR =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏦 Risk Motoru + Drawdown Kalkanı Aktif")


async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Rapor hazırlanıyor...")

    filename, text = generate_weekly_report()

    if filename:
        with open(filename, "rb") as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f
            )

    await update.message.reply_text(text)


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Kullanım: /balance 150000")
        return

    try:
        amount = int(context.args[0])
        save_balance(amount)
        await update.message.reply_text(f"✅ Yeni portföy: {amount} TL")
    except:
        await update.message.reply_text("Geçersiz değer.")


async def close(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) != 2:
        await update.message.reply_text("Kullanım: /close EREGL -1.0")
        return

    symbol = context.args[0] + ".IS"
    rr = float(context.args[1])

    new_balance = close_trade(symbol, rr)

    await update.message.reply_text(
        f"✅ İşlem kapandı.\nYeni Bakiye: {round(new_balance,2)} TL"
    )


async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_equity_report())


# ================= OTOMATİK SABAH RAPOR =================

async def morning_job(context: ContextTypes.DEFAULT_TYPE):

    chat_id = context.job.chat_id

    filename, text = generate_weekly_report()

    if filename:
        with open(filename, "rb") as f:
            await context.bot.send_document(chat_id=chat_id, document=f)

    await context.bot.send_message(chat_id=chat_id, text=text)


# ================= MAIN =================

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weekly", weekly))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("close", close))
    app.add_handler(CommandHandler("equity", equity))

    # Sabah 09:15 otomatik rapor
    app.job_queue.run_daily(
        morning_job,
        time=time(hour=9, minute=15),
        days=(0,1,2,3,4),
        name="morning_report",
        chat_id=None  # İlk start atan kullanıcıya bağlanacak
    )

    app.run_polling()


if __name__ == "__main__":
    main()
