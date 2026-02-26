import os
from datetime import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from institutional_engine import (
    generate_weekly_report,
    save_balance,
    close_trade,
    generate_equity_chart,
    check_intraday_alerts
)

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏦 Profesyonel Risk Motoru Aktif")

async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Rapor hazırlanıyor...")
    filename, text = generate_weekly_report()
    if filename:
        with open(filename, "rb") as f:
            await context.bot.send_document(update.effective_chat.id, f)
    await update.message.reply_text(text)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = int(context.args[0])
    save_balance(amount)
    await update.message.reply_text(f"Yeni bakiye: {amount}")

async def close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = context.args[0] + ".IS"
    rr = float(context.args[1])
    new_balance = close_trade(symbol, rr)
    await update.message.reply_text(f"Yeni bakiye: {round(new_balance,2)}")

async def equitycurve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filename, text = generate_equity_chart()
    if filename:
        with open(filename, "rb") as f:
            await context.bot.send_photo(update.effective_chat.id, f)
    await update.message.reply_text(text)

async def morning_job(context: ContextTypes.DEFAULT_TYPE):
    filename, text = generate_weekly_report()
    if filename:
        with open(filename, "rb") as f:
            await context.bot.send_document(context.job.chat_id, f)
    await context.bot.send_message(context.job.chat_id, text)

async def intraday_job(context: ContextTypes.DEFAULT_TYPE):
    messages = check_intraday_alerts()
    for msg in messages:
        await context.bot.send_message(context.job.chat_id, msg)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weekly", weekly))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("close", close))
    app.add_handler(CommandHandler("equitycurve", equitycurve))

    app.job_queue.run_daily(morning_job, time=time(9,15))
    app.job_queue.run_repeating(intraday_job, interval=600)

    app.run_polling()

if __name__ == "__main__":
    main()
