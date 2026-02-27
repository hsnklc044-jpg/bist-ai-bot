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
        "/scan → Günlük trade planı\n"
        "/backtestmc → Monte Carlo risk testi\n"
    )


# ================= SCAN =================

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        await update.message.reply_text("📊 Tarama başlatıldı...")

        result = scan_trades()

        regime = result.get("regime", {})
        trades = result.get("trades", [])

        regime_name = regime.get("regime", "UNKNOWN")
        risk_percent = round(regime.get("risk", 0) * 100, 2)
        max_trades = regime.get("max_trades", 0)

        message = (
            f"🟢 {regime_name} REJİM\n"
            f"Risk: %{risk_percent}\n"
            f"Max Trade: {max_trades}\n\n"
        )

        if not trades:
            message += "Uygun trade bulunamadı."
        else:
            message += "Seçilen Trade Planları:\n\n"

            for i, trade in enumerate(trades, 1):
                message += (
                    f"{i}. {trade['symbol']}\n"
                    f"   Fiyat: {trade['price']}\n"
                    f"   🚀 Entry: {trade['breakout_entry']}\n"
                    f"   🛑 Stop: {trade['stop']}\n"
                    f"   🎯 Target: {trade['target']}\n"
                    f"   📊 R/R: {trade['rr']}\n"
                    f"   💰 Lot: {trade['lot']}\n"
                    f"   💵 Pozisyon: {trade['position_value']} TL\n\n"
                )

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"❌ SCAN HATA: {str(e)}")
        print("SCAN ERROR:", e)


# ================= MONTE CARLO =================

async def backtestmc(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        await update.message.reply_text("🎲 Monte Carlo simülasyonu çalışıyor...")

        results, error = run_monte_carlo(300)

        if error:
            await update.message.reply_text(error)
            return

        message = "📊 MONTE CARLO RAPOR\n\n"

        for k, v in results.items():
            message += f"{k}: {v}\n"

        try:
            with open("montecarlo_dd.png", "rb") as f:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=f
                )
        except:
            pass

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"❌ MC HATA: {str(e)}")
        print("MC ERROR:", e)


# ================= SABAH OTOMATİK TARAMA =================

async def morning_job(context: ContextTypes.DEFAULT_TYPE):

    try:
        result = scan_trades()
        trades = result.get("trades", [])

        message = "🌅 Sabah Trade Planı\n\n"

        if not trades:
            message += "Bugün uygun setup yok."
        else:
            for trade in trades:
                message += (
                    f"{trade['symbol']}\n"
                    f"🚀 {trade['breakout_entry']} | "
                    f"🛑 {trade['stop']} | "
                    f"🎯 {trade['target']}\n"
                    f"💰 Lot: {trade['lot']}\n\n"
                )

        # Chat ID'yi ilk kullanıcıdan al
        chat_id = context.job.chat_id
        await context.bot.send_message(chat_id=chat_id, text=message)

    except Exception as e:
        print("MORNING JOB ERROR:", e)


# ================= MAIN =================

def main():

    if not TOKEN:
        print("BOT_TOKEN bulunamadı!")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(CommandHandler("backtestmc", backtestmc))

    # Sabah 09:15 otomatik plan
    try:
        app.job_queue.run_daily(
            morning_job,
            time=time(9, 15)
        )
    except Exception as e:
        print("JOB QUEUE ERROR:", e)

    print("Bot başlatıldı...")
    app.run_polling()


if __name__ == "__main__":
    main()
