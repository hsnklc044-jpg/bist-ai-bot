import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from performance_tracker import get_performance_report, run_monte_carlo
from risk_engine import get_risk_metrics

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable not set.")


# ---------------- COMMANDS ---------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🚀 Institutional Portfolio Engine (Stable Core) aktif.\n\n"
        "Komutlar:\n"
        "/report\n"
        "/risk\n"
        "/montecarlo"
    )
    await update.message.reply_text(message)


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = get_performance_report()

        message = (
            "📊 PERFORMANS RAPORU\n\n"
            f"Toplam İşlem: {data['total_trades']}\n"
            f"Kazanan: {data['wins']}\n"
            f"Kaybeden: {data['losses']}\n"
            f"Net Kar: {data['net_profit']} TL\n"
            f"Güncel Equity: {data['current_equity']} TL"
        )

        await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Report error: {e}")
        await update.message.reply_text("❌ Report hesaplanamadı.")


async def risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = get_risk_metrics()

        message = (
            "📈 RISK METRICS PANEL\n\n"
            f"Win Rate: {data['win_rate']}%\n"
            f"Profit Factor: {data['profit_factor']}\n"
            f"Avg Win: {data['avg_win']} TL\n"
            f"Avg Loss: {data['avg_loss']} TL\n"
            f"Expectancy: {data['expectancy']} TL\n"
            f"Sharpe Ratio: {data['sharpe_ratio']}"
        )

        await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Risk error: {e}")
        await update.message.reply_text("❌ Risk hesaplanamadı.")


async def montecarlo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        result = run_monte_carlo()

        message = (
            "🎲 MONTE CARLO SİMÜLASYONU\n\n"
            f"Ortalama Final Equity: {result['mean_equity']} TL\n"
            f"En İyi Senaryo: {result['best_case']} TL\n"
            f"En Kötü Senaryo: {result['worst_case']} TL\n"
            f"Ruin Olasılığı: %{result['ruin_probability']}"
        )

        await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Monte Carlo error: {e}")
        await update.message.reply_text("❌ Monte Carlo hesaplanamadı.")


# ---------------- MAIN ---------------- #

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("report", report))
    application.add_handler(CommandHandler("risk", risk))
    application.add_handler(CommandHandler("montecarlo", montecarlo))

    logger.info("Institutional Portfolio Engine Stable Core başlatıldı...")
    application.run_polling()


if __name__ == "__main__":
    main()
