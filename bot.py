import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from performance_tracker import (
    get_performance_report,
    generate_equity_chart,
    get_risk_metrics,
)

from risk_engine import (
    log_trade,
    calculate_position_size,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# =========================
# COMMANDS
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Institutional Portfolio Engine v4 aktif.\n"
        "Komutlar:\n"
        "/report\n"
        "/equity\n"
        "/risk\n"
        "/testtrade\n"
        "/position STOP_DISTANCE"
    )


# -------------------------
# PERFORMANCE REPORT
# -------------------------

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        report_data = get_performance_report()

        message = (
            "📊 PERFORMANS RAPORU\n\n"
            f"Toplam İşlem: {report_data['total_trades']}\n"
            f"Kazanan: {report_data['wins']}\n"
            f"Kaybeden: {report_data['losses']}\n"
            f"Net Kar: {report_data['net_profit']} TL\n"
            f"Güncel Equity: {report_data['equity']} TL"
        )

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"❌ Hata:\n{str(e)}")


# -------------------------
# TEST TRADE
# -------------------------

async def testtrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        profit = log_trade(
            symbol="BIST30",
            side="long",
            entry_price=100,
            exit_price=110,
            quantity=10
        )

        await update.message.reply_text(
            f"✅ Test trade eklendi.\nKar: {profit} TL"
        )

    except Exception as e:
        await update.message.reply_text(str(e))


# -------------------------
# EQUITY CURVE
# -------------------------

async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chart, max_dd = generate_equity_chart()

        if chart is None:
            await update.message.reply_text("Henüz işlem yok.")
            return

        await update.message.reply_photo(
            photo=chart,
            caption=f"📈 Equity Curve\nMax Drawdown: {max_dd}%"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Grafik üretilemedi:\n{str(e)}")


# -------------------------
# RISK PANEL
# -------------------------

async def risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        metrics = get_risk_metrics()

        if metrics is None:
            await update.message.reply_text("Henüz işlem yok.")
            return

        message = (
            "📊 RISK METRICS PANEL\n\n"
            f"Toplam İşlem: {metrics['total_trades']}\n"
            f"Win Rate: {metrics['win_rate']}%\n"
            f"Profit Factor: {metrics['profit_factor']}\n"
            f"Avg Win: {metrics['avg_win']} TL\n"
            f"Avg Loss: {metrics['avg_loss']} TL\n"
            f"Expectancy: {metrics['expectancy']} TL\n"
            f"Sharpe Ratio: {metrics['sharpe']}"
        )

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"❌ Risk hesaplanamadı:\n{str(e)}")


# -------------------------
# POSITION SIZE CALCULATOR
# -------------------------

async def position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Kullanım: /position STOP_DISTANCE")
        return

    try:
        stop_distance = float(context.args[0])

        if stop_distance <= 0:
            await update.message.reply_text("Stop mesafesi 0'dan büyük olmalı.")
            return

        size = calculate_position_size(stop_distance)

        await update.message.reply_text(
            f"📐 Position Size: {size} lot\n"
            f"Risk per trade: %2"
        )

    except:
        await update.message.reply_text("Geçersiz değer.")


# =========================
# MAIN
# =========================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("testtrade", testtrade))
    app.add_handler(CommandHandler("equity", equity))
    app.add_handler(CommandHandler("risk", risk))
    app.add_handler(CommandHandler("position", position))

    logger.info("Institutional Portfolio Engine v4 başlatıldı...")

    app.run_polling()


if __name__ == "__main__":
    main()
