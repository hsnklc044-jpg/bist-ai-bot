import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from performance_tracker import (
    get_performance_report,
    get_risk_metrics,
    generate_equity_chart,
    monte_carlo_simulation,
)

from risk_engine import (
    calculate_position_size,
    log_trade,
)

TOKEN = os.getenv("BOT_TOKEN")


# ==================================================
# START
# ==================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = (
        "🤖 Institutional Portfolio Engine v7 aktif.\n\n"
        "Komutlar:\n"
        "/report\n"
        "/equity\n"
        "/risk\n"
        "/montecarlo\n"
        "/position STOP_DISTANCE RISK_PERCENT\n"
        "/stresstest"
    )

    await update.message.reply_text(message)


# ==================================================
# REPORT
# ==================================================

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        data = get_performance_report()

        text = (
            "📊 PERFORMANS RAPORU\n\n"
            f"Toplam İşlem: {data['total_trades']}\n"
            f"Kazanan: {data['wins']}\n"
            f"Kaybeden: {data['losses']}\n"
            f"Net Kar: {data['net_profit']} TL\n"
            f"Güncel Equity: {data['equity']} TL"
        )

        await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text(f"❌ Report hata: {str(e)}")


# ==================================================
# EQUITY
# ==================================================

async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        chart = generate_equity_chart()
        await update.message.reply_photo(chart)

    except Exception as e:
        await update.message.reply_text(f"❌ Equity hata: {str(e)}")


# ==================================================
# RISK
# ==================================================

async def risk(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        data = get_risk_metrics()

        text = (
            "📊 RISK METRICS PANEL\n\n"
            f"Toplam İşlem: {data['total_trades']}\n"
            f"Win Rate: {data['win_rate']}%\n"
            f"Profit Factor: {data['profit_factor']}\n"
            f"Avg Win: {data['avg_win']} TL\n"
            f"Avg Loss: {data['avg_loss']} TL\n"
            f"Expectancy: {data['expectancy']} TL\n"
            f"Sharpe Ratio: {data['sharpe']}"
        )

        await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text(f"❌ Risk hata: {str(e)}")


# ==================================================
# MONTE CARLO
# ==================================================

async def montecarlo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        data = monte_carlo_simulation()

        text = (
            "🎲 MONTE CARLO ANALYSIS\n\n"
            f"Ortalama Final Equity: {data['avg_final_equity']} TL\n"
            f"En Kötü Senaryo Equity: {data['worst_equity']} TL\n"
            f"Ortalama Drawdown: {data['avg_drawdown']}%\n"
            f"En Kötü Drawdown: {data['worst_drawdown']}%\n"
            f"Risk of Ruin: {data['risk_of_ruin']}"
        )

        await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text(f"❌ Monte Carlo hata: {str(e)}")


# ==================================================
# POSITION SIZE
# ==================================================

async def position(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        stop_distance = float(context.args[0])
        risk_percent = float(context.args[1])

        size = calculate_position_size(stop_distance, risk_percent)

        await update.message.reply_text(
            f"📐 Position Size: {size} lot\n"
            "Adaptive Portfolio Risk Engine aktif."
        )

    except:
        await update.message.reply_text(
            "Kullanım: /position STOP_DISTANCE RISK_PERCENT"
        )


# ==================================================
# STRESS TEST
# ==================================================

async def stresstest(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        stress_sequence = [-100] * 10 + [100] * 5

        for p in stress_sequence:
            log_trade(p)

        await update.message.reply_text(
            "✅ Stress test trade seti eklendi. (+15 işlem)"
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Stress test hata: {str(e)}"
        )


# ==================================================
# MAIN
# ==================================================

def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("equity", equity))
    app.add_handler(CommandHandler("risk", risk))
    app.add_handler(CommandHandler("montecarlo", montecarlo))
    app.add_handler(CommandHandler("position", position))
    app.add_handler(CommandHandler("stresstest", stresstest))

    print("Institutional Portfolio Engine v7 başlatıldı...")
    app.run_polling()


if __name__ == "__main__":
    main()
