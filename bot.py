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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏦 AI Trading Desk Aktif\n\n"
        "/scan → Günlük trade planı\n"
        "/backtestmc → Monte Carlo testi\n"
    )


async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("📊 Tarama başlatıldı...")

    result = scan_trades()

    regime = result.get("regime", {})
    trades = result.get("trades", [])

    regime_name = regime.get("regime", "UNKNOWN")
    risk_percent = round(regime.get("risk", 0) * 100, 2)
    daily_risk = regime.get("daily_risk_used", 0)
    max_trades = regime.get("max_trades", 0)

    message = (
        f"🟢 {regime_name} REJİM\n"
        f"Risk: %{risk_percent}\n"
        f"Günlük Risk Kullanımı: %{daily_risk}\n"
        f"Trade Sayısı: {max_trades}\n\n"
    )

    if not trades:
        message += "Uygun trade bulunamadı."
    else:
        for i, trade in enumerate(trades, 1):
            message += (
                f"{i}. {trade['symbol']}\n"
                f"Fiyat: {trade['price']}\n"
                f"Entry: {trade['entry']}\n"
                f"Stop: {trade['stop']}\n"
                f"Target: {trade['target']}\n"
                f"R/R: {trade['rr']}\n"
                f"Lot: {trade['lot']}\n"
                f"Pozisyon: {trade['position_value']} TL\n\n"
            )

    await update.message.reply_text(message)


async def backtestmc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎲 Monte Carlo çalışıyor...")

    results, error = run_monte_carlo(300)

    if error:
        await update.message.reply_text(error)
        return

    message = "📊 MONTE CARLO RAPOR\n\n"
    for k, v in results.items():
        message += f"{k}: {v}\n"

    await update.message.reply_text(message)


def main():

    if not TOKEN:
        print("BOT_TOKEN bulunamadı!")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(CommandHandler("backtestmc", backtestmc))

    print("Bot başlatıldı...")
    app.run_polling()


if __name__ == "__main__":
    main()
