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
    check_daily_status,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable not set.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Institutional Portfolio Engine\n\n"
        "/report\n"
        "/montecarlo\n"
        "/equity\n"
        "/riskstatus\n"
        "/position\n"
        "/dailystatus"
    )


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_performance_report()
    await update.message.reply_text(
        f"📊 REPORT\n\n"
        f"Net Profit: {data['net_profit']} TL\n"
        f"Equity: {data['current_equity']} TL\n"
        f"Max DD: {data['max_drawdown']} TL\n"
        f"DD %: {data['drawdown_percent']}%"
    )


async def montecarlo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = run_monte_carlo()
    await update.message.reply_text(
        f"🎲 MONTE CARLO\n\n"
        f"Mean: {result['mean_equity']} TL\n"
        f"Best: {result['best_case']} TL\n"
        f"Worst: {result['worst_case']} TL\n"
        f"Ruin: %{result['ruin_probability']}"
    )


async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chart = generate_equity_chart()
    if chart:
        await update.message.reply_photo(photo=chart)
    else:
        await update.message.reply_text("Henüz veri yok.")


async def riskstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status, dd = check_risk_level()
    await update.message.reply_text(f"Risk Status: {status}\nDrawdown: {dd}%")


async def position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    multiplier = get_position_multiplier()
    await update.message.reply_text(f"Position Multiplier: {multiplier}x")


async def dailystatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status, daily = check_daily_status()
    await update.message.reply_text(
        f"📅 DAILY STATUS\n\n"
        f"Status: {status}\n"
        f"Daily %: {daily}%"
    )


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("montecarlo", montecarlo))
    app.add_handler(CommandHandler("equity", equity))
    app.add_handler(CommandHandler("riskstatus", riskstatus))
    app.add_handler(CommandHandler("position", position))
    app.add_handler(CommandHandler("dailystatus", dailystatus))

    app.run_polling()


if __name__ == "__main__":
    main()
