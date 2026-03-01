import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from performance_tracker import (
    get_performance_report,
    run_monte_carlo,
    generate_equity_chart,
    calculate_drawdown,
    check_risk_level,
    get_position_multiplier,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable not set.")


# =====================================================
# COMMANDS
# =====================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🚀 Institutional Portfolio Engine\n\n"
        "Komutlar:\n"
        "/report\n"
        "/montecarlo\n"
        "/equity\n"
        "/riskstatus\n"
        "/position"
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
            f"Güncel Equity: {data['current_equity']} TL\n"
            f"Max Drawdown: {data['max_drawdown']} TL\n"
            f"Drawdown %: {data['drawdown_percent']}%"
        )

        await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Report error: {e}")
        await update.message.reply_text("❌ Report hesaplanamadı.")


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


async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chart = generate_equity_chart()

        if chart is None:
            await update.message.reply_text("📭 Henüz trade verisi yok.")
            return

        max_dd, dd_percent = calculate_drawdown()

        caption = (
            "📈 EQUITY CURVE\n\n"
            f"Max Drawdown: {max_dd} TL\n"
            f"Drawdown %: {dd_percent}%"
        )

        await update.message.reply_photo(photo=chart, caption=caption)

    except Exception as e:
        logger.error(f"Equity error: {e}")
        await update.message.reply_text("❌ Equity grafiği üretilemedi.")


async def riskstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        status, dd_percent = check_risk_level()

        await update.message.reply_text(
            f"📊 RISK STATUS\n\nDurum: {status}\nDrawdown: {dd_percent}%"
        )

    except Exception as e:
        logger.error(f"Risk status error: {e}")
        await update.message.reply_text("❌ Risk status hesaplanamadı.")


async def position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        multiplier = get_position_multiplier()
        status, dd_percent = check_risk_level()

        message = (
            "📏 POSITION CONTROL\n\n"
            f"Risk Status: {status}\n"
            f"Drawdown: {dd_percent}%\n"
            f"Position Multiplier: {multiplier}x"
        )

        await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Position error: {e}")
        await update.message.reply_text("❌ Position kontrolü başarısız.")


# =====================================================
# MAIN
# =====================================================

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("report", report))
    application.add_handler(CommandHandler("montecarlo", montecarlo))
    application.add_handler(CommandHandler("equity", equity))
    application.add_handler(CommandHandler("riskstatus", riskstatus))
    application.add_handler(CommandHandler("position", position))

    logger.info("Institutional Portfolio Engine başlatıldı...")
    application.run_polling()


if __name__ == "__main__":
    main()
