import os
from datetime import time
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from institutional_engine import scan_trades
from backtest_engine import run_monte_carlo


TOKEN = os.getenv("BOT_TOKEN")


# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏦 AI Trading Desk Aktif\n\n"
        "Komutlar:\n"
        "/scan → Günlük tarama\n"
        "/backtestmc → Monte Carlo risk testi\n"
    )


# ================= SCAN =================

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("📊 Tarama başlatıldı...")

    result = scan_trades()
    regime = result["regime"]

    regime_name = regime["regime"]
    risk_percent = round(regime["risk"] * 100, 2)
    max_trades = regime["max_trades"]

    # 🔴 KRİZ MODU
    if regime_name == "CRISIS":
        await update.message.reply_text(
            "🔴 KRİZ MODU\n\n"
            "Yeni işlem açılmaz.\n"
            "Açık pozisyonları %50 azalt.\n"
        )
        return

    trades = result.get("trades", [])

    if not trades:
        await update.message.reply_text(
            f"🟡 {regime_name} REJİM\n"
            f"Risk: %{risk_percent}\n"
            f"Max Trade: {max_trades}\n\n"
            "Uygun trade bulunamadı."
        )
        return

    message = (
        f"🟢 {regime_name} REJİM\n"
        f"Risk: %{risk_percent}\n"
        f"Max Trade: {max_trades}\n\n"
        "Seçilen Trade'ler:\n\n"
    )

    for i, trade in enumerate(trades, 1):
        message += (
            f"{i}. {trade['symbol']}\n"
            f"   Fiyat: {trade['price']}\n"
            f"   R/R: {trade['rr']}\n"
            f"   Skor: {trade['score']}\n\n"
        )

    await update.message.reply_text(message)


# ================= MONTE CARLO =================

async def backtestmc(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("🎲 Monte Carlo simülasyonu çalışıyor...")

    results, error = run_monte_carlo(1000)

    if error:
        await update.message.reply_text(error)
        return

    message = "📊 MONTE CARLO RAPOR\n\n"

    for k, v in results.items():
        message += f"{k}: {v}\n"

    with open("montecarlo_dd.png", "rb") as f:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=f
        )

    await update.message.reply_text(message)


# ================= SABAH OTOMATİK =================

async def morning_job(context: ContextTypes.DEFAULT_TYPE):

    result = scan_trades()
    regime = result["regime"]

    regime_name = regime["regime"]
    risk_percent = round(regime["risk"] * 100, 2)
    max_trades = regime["max_trades"]

    if regime_name == "CRISIS":
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text="🔴 KRİZ MODU\nYeni işlem yok.\nAçık pozisyonları azalt."
        )
        return

    trades = result.get("trades", [])

    if not trades:
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=f"🟡 {regime_name} REJİM\nRisk: %{risk_percent}\nTrade yok."
        )
        return

    message = (
        f"🟢 {regime_name} REJİM\n"
        f"Risk: %{risk_percent}\n"
        f"Max Trade: {max_trades}\n\n"
    )

    for i, trade in enumerate(trades, 1):
        message += (
            f"{i}. {trade['symbol']} | "
            f"Fiyat: {trade['price']} | "
            f"R/R: {trade['rr']}\n"
        )

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=message
    )


# ================= MAIN =================

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(CommandHandler("backtestmc", backtestmc))

    # Sabah 09:15 otomatik tarama
    app.job_queue.run_daily(
        morning_job,
        time=time(9, 15)
    )

    app.run_polling()


if __name__ == "__main__":
    main()
