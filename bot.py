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
        "/scan → Günlük trade planı\n"
        "/balance → Anlık performans\n"
    )

# ================= SCAN =================
async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("📊 Tarama başlatıldı...")

    result = scan_trades()
    regime = result.get("regime", {})
    trades = result.get("trades", [])

    regime_name = regime.get("regime", "UNKNOWN")
    risk_percent = round(regime.get("risk", 0) * 100, 2)
    daily_risk = regime.get("daily_risk_used", 0)

    message = (
        f"🟢 {regime_name} REJİM\n"
        f"Risk: %{risk_percent}\n"
        f"Günlük Risk Kullanımı: %{daily_risk}\n\n"
    )

    if not trades:
        message += "Uygun trade bulunamadı."
    else:
        for i, trade in enumerate(trades, 1):

            log_trade(trade)

            message += (
                f"{i}. {trade['symbol']}\n"
                f"Entry: {trade['entry']}\n"
                f"Stop: {trade['stop']}\n"
                f"Target: {trade['target']}\n"
                f"R/R: {trade['rr']}\n"
                f"Lot: {trade['lot']}\n\n"
            )

    await update.message.reply_text(message)

# ================= BALANCE =================
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    equity = get_balance()
    graph_file = generate_equity_graph()
    metrics = performance_metrics()

    message = f"💰 Equity: {equity} TL\n\n"

    for k, v in metrics.items():
        message += f"{k}: {v}\n"

    await update.message.reply_text(message)

    with open(graph_file, "rb") as photo:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo
        )

# ================= MORNING AUTO REPORT =================
async def morning_report(context: ContextTypes.DEFAULT_TYPE):

    equity = get_balance()
    graph_file = generate_equity_graph()
    metrics = performance_metrics()

    message = f"🌅 GÜNLÜK PERFORMANS RAPORU\n\n"
    message += f"Equity: {equity} TL\n\n"

    for k, v in metrics.items():
        message += f"{k}: {v}\n"

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=message
    )

    with open(graph_file, "rb") as photo:
        await context.bot.send_photo(
            chat_id=context.job.chat_id,
            photo=photo
        )

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

    # ⏰ Sabah 09:00 otomatik rapor
    app.job_queue.run_daily(
        morning_report,
        time=time(9, 0)
    )

    print("Institutional Bot başlatıldı...")
    app.run_polling()

if __name__ == "__main__":
    main()
