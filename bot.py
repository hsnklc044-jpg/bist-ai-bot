import os
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
    generate_equity_chart,
    check_intraday_alerts
)

from backtest_engine import run_backtest


TOKEN = os.getenv("BOT_TOKEN")


# ================= BASIC COMMANDS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏦 AI Trading Desk Aktif\n"
        "Komutlar:\n"
        "/weekly\n"
        "/balance 150000\n"
        "/close EREGL 2.0\n"
        "/equitycurve\n"
        "/backtest"
    )


# ================= SABAH RAPOR =================

async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("📊 Sabah raporu hazırlanıyor...")

    filename, text = generate_weekly_report()

    if filename:
        with open(filename, "rb") as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f
            )

    await update.message.reply_text(text)


# ================= BALANCE =================

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Kullanım: /balance 150000")
        return

    try:
        amount = int(context.args[0])
        save_balance(amount)
        await update.message.reply_text(f"💰 Yeni Bakiye: {amount} TL")
    except:
        await update.message.reply_text("Geçersiz değer.")


# ================= CLOSE TRADE =================

async def close(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) != 2:
        await update.message.reply_text("Kullanım: /close EREGL 2.0")
        return

    symbol = context.args[0] + ".IS"
    rr = float(context.args[1])

    new_balance = close_trade(symbol, rr)

    await update.message.reply_text(
        f"✅ İşlem kapandı.\nYeni Bakiye: {round(new_balance,2)} TL"
    )


# ================= EQUITY CURVE =================

async def equitycurve(update: Update, context: ContextTypes.DEFAULT_TYPE):

    filename, text = generate_equity_chart()

    if filename:
        with open(filename, "rb") as f:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=f
            )

    await update.message.reply_text(text)


# ================= BACKTEST =================

async def backtest(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("⏳ 3 yıllık backtest çalışıyor...")

    results = run_backtest(3)

    message = "📊 BACKTEST RAPOR\n\n"

    for k, v in results.items():
        message += f"{k}: {v}\n"

    with open("backtest_equity.png", "rb") as f:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=f
        )

    await update.message.reply_text(message)


# ================= OTOMATİK SABAH JOB =================

async def morning_job(context: ContextTypes.DEFAULT_TYPE):

    filename, text = generate_weekly_report()

    if filename:
        with open(filename, "rb") as f:
            await context.bot.send_document(
                chat_id=context.job.chat_id,
                document=f
            )

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=text
    )


# ================= GÜN İÇİ ALARM JOB =================

async def intraday_job(context: ContextTypes.DEFAULT_TYPE):

    messages = check_intraday_alerts()

    for msg in messages:
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=msg
        )


# ================= MAIN =================

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    # Komutlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weekly", weekly))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("close", close))
    app.add_handler(CommandHandler("equitycurve", equitycurve))
    app.add_handler(CommandHandler("backtest", backtest))

    # Sabah 09:15
    app.job_queue.run_daily(
        morning_job,
        time=time(9, 15)
    )

    # 10 dakikada bir alarm
    app.job_queue.run_repeating(
        intraday_job,
        interval=600,
        first=60
    )

    app.run_polling()


if __name__ == "__main__":
    main()
