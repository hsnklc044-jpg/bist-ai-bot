import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from performance_tracker import (
    get_performance_report,
    generate_equity_chart,
    get_risk_metrics,
    monte_carlo_simulation
)

from risk_engine import (
    calculate_position_size,
    log_trade
)

TOKEN = os.getenv("BOT_TOKEN")


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🤖 Institutional Portfolio Engine v6 aktif.\n\n"
        "/report\n"
        "/equity\n"
        "/risk\n"
        "/montecarlo\n"
        "/position STOP VOL\n"
        "/stresstest"
    )
    await update.message.reply_text(message)


# =========================
# REPORT
# =========================

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_performance_report()

    message = (
        "📊 PERFORMANS RAPORU\n\n"
        f"Toplam İşlem: {data['total_trades']}\n"
        f"Kazanan: {data['wins']}\n"
        f"Kaybeden: {data['losses']}\n"
        f"Net Kar: {data['net_profit']} TL\n"
        f"Güncel Equity: {data['equity']} TL"
    )

    await update.message.reply_text(message)


# =========================
# EQUITY
# =========================

async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chart, max_dd = generate_equity_chart()

    if chart is None:
        await update.message.reply_text("Henüz yeterli veri yok.")
        return

    await update.message.reply_photo(
        photo=chart,
        caption=f"📈 Equity Curve\nMax Drawdown: {max_dd}%"
    )


# =========================
# RISK PANEL
# =========================

async def risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    metrics = get_risk_metrics()

    if metrics is None:
        await update.message.reply_text("Henüz yeterli veri yok.")
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


# =========================
# MONTE CARLO
# =========================

async def montecarlo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = monte_carlo_simulation()

    if result is None:
        await update.message.reply_text("Henüz yeterli veri yok.")
        return

    message = (
        "🎲 MONTE CARLO ANALYSIS\n\n"
        f"Ortalama Final Equity: {result['avg_final_equity']} TL\n"
        f"En Kötü Senaryo Equity: {result['worst_case_equity']} TL\n"
        f"Ortalama Drawdown: {result['avg_drawdown']}%\n"
        f"En Kötü Drawdown: {result['worst_drawdown']}%\n"
        f"Risk of Ruin: {result['risk_of_ruin_%']}%"
    )

    await update.message.reply_text(message)


# =========================
# POSITION SIZE
# =========================

async def position(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) != 2:
        await update.message.reply_text(
            "Kullanım: /position STOP_DISTANCE VOLATILITY"
        )
        return

    try:
        stop_distance = float(context.args[0])
        volatility = float(context.args[1])

        size = calculate_position_size(stop_distance, volatility)

        await update.message.reply_text(
            f"📐 Position Size: {size} lot\n"
            f"Volatility + Drawdown Adjusted Risk"
        )

    except Exception as e:
        await update.message.reply_text(str(e))


# =========================
# STRESS TEST
# =========================

async def stresstest(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # 5 karlı trade
    for _ in range(5):
        log_trade("TEST", "long", 100, 110, 10)

    # 5 zararlı trade
    for _ in range(5):
        log_trade("TEST", "long", 100, 90, 10)

    await update.message.reply_text("✅ Stress test trade seti eklendi.")


# =========================
# MAIN
# =========================

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("equity", equity))
    app.add_handler(CommandHandler("risk", risk))
    app.add_handler(CommandHandler("montecarlo", montecarlo))
    app.add_handler(CommandHandler("position", position))
    app.add_handler(CommandHandler("stresstest", stresstest))

    print("Institutional Portfolio Engine v6 başlatıldı...")
    app.run_polling()


if __name__ == "__main__":
    main()
