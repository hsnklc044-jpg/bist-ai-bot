import os
from datetime import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from institutional_engine import scan_trades
from performance_tracker import (
    init_log,
    log_trade,
    get_balance,
    generate_equity_graph,
    performance_metrics
)

TOKEN = os.getenv("BOT_TOKEN")


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏦 Institutional Trading Desk Aktif\n\n"
        "/scan → Institutional portfolio dağılımı\n"
        "/balance → Anlık performans\n"
    )


# ================= SCAN =================
async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("📊 Institutional Scan başlatıldı...")

    try:
        result = scan_trades()

        if not result:
            await update.message.reply_text("Engine cevap vermedi.")
            return

        if "error" in result:
            await update.message.reply_text(result["error"])
            return

        portfolio = result.get("portfolio", {})
        trades = result.get("trades", [])

        message = (
            f"📈 MODEL: {portfolio.get('model','-')}\n"
            f"Beklenen Getiri: %{portfolio.get('expected_return_%',0)}\n"
            f"Volatilite: %{portfolio.get('volatility_%',0)}\n"
            f"Sharpe: {portfolio.get('sharpe_ratio',0)}\n"
            f"Leverage: {portfolio.get('leverage',0)}\n\n"
        )

        if not trades:
            message += "Uygun trade bulunamadı."
        else:
            message += "📌 Trade Dağılımı:\n\n"

            for t in trades:

                log_trade(t)

                message += (
                    f"{t['symbol']}\n"
                    f"Ağırlık: %{t['weight_%']}\n"
                    f"Lot: {t['lot']}\n"
                    f"Tutar: {t['allocation']} TL\n\n"
                )

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"❌ SCAN HATA: {str(e)}")
        print("SCAN ERROR:", e)


# ================= BALANCE =================
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        balance_data = get_balance()
        metrics = performance_metrics()

        message = (
            "📊 PORTFÖY DURUMU\n\n"
            f"Toplam Equity: {balance_data.get('equity',0)} TL\n"
            f"Günlük PnL: {balance_data.get('daily_pnl',0)} TL\n"
            f"Toplam PnL: {balance_data.get('total_pnl',0)} TL\n\n"
            f"Max Drawdown: %{metrics.get('max_drawdown',0)}\n"
            f"Sharpe: {metrics.get('sharpe',0)}\n"
        )

        await update.message.reply_text(message)

        try:
            generate_equity_graph()
            with open("equity_curve.png", "rb") as f:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=f
                )
        except:
            pass

    except Exception as e:
        await update.message.reply_text(f"❌ BALANCE HATA: {str(e)}")
        print("BALANCE ERROR:", e)


# ================= SABAH OTOMATİK =================
async def morning_job(context: ContextTypes.DEFAULT_TYPE):

    try:
        result = scan_trades()
        trades = result.get("trades", [])

        message = "🌅 Sabah Institutional Plan\n\n"

        if not trades:
            message += "Bugün uygun dağılım yok."
        else:
            for t in trades:
                message += (
                    f"{t['symbol']} → "
                    f"%{t['weight_%']} | "
                    f"Lot: {t['lot']}\n"
                )

        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=message
        )

    except Exception as e:
        print("MORNING JOB ERROR:", e)


# ================= MAIN =================
def main():

    if not TOKEN:
        print("BOT_TOKEN bulunamadı!")
        return

    init_log()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(CommandHandler("balance", balance))

    try:
        app.job_queue.run_daily(
            morning_job,
            time=time(9, 15)
        )
    except Exception as e:
        print("JOB ERROR:", e)

    print("Institutional Bot başlatıldı...")
    app.run_polling()


if __name__ == "__main__":
    main()
