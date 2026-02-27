import os
from datetime import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from institutional_engine import scan_trades
from performance_tracker import (
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
        "/scan → Portfolio dağılımı\n"
        "/balance → Performans durumu\n"
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

                # trade log kaydı
                try:
                    log_trade(t)
                except:
                    pass

                message += (
                    f"{t.get('symbol','-')}\n"
                    f"Ağırlık: %{t.get('weight_%',0)}\n"
                    f"Lot: {t.get('lot',0)}\n"
                    f"Tutar: {t.get('allocation',0)} TL\n\n"
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

        # grafik varsa gönder
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


# ================= MAIN =================
def main():

    if not TOKEN:
        print("BOT_TOKEN bulunamadı!")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(CommandHandler("balance", balance))

    print("Institutional Bot başlatıldı...")
    app.run_polling()


if __name__ == "__main__":
    main()
