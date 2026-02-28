import os
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from performance_tracker import (
    log_trade,
    risk_check,
    get_balance_summary
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

SYMBOLS = ["EREGL.IS", "SISE.IS", "KCHOL.IS", "THYAO.IS", "BIMAS.IS"]

# ===============================
# SCAN COMMAND
# ===============================

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("📊 Institutional Scan başlatıldı...")

    new_trades = 0

    for symbol in SYMBOLS:

        price_data = yf.download(symbol, period="1d", auto_adjust=True, progress=False)

        if price_data is None or price_data.empty:
            continue

        close_series = price_data["Close"]

        if hasattr(close_series, "iloc"):
            price = float(close_series.iloc[-1])
        else:
            price = float(close_series)

        allocation = 20000
        lot = allocation / price
        stop_distance = price * 0.02

        # RISK CHECK
        allowed, reason = risk_check(symbol, allocation)

        if not allowed:
            print(f"RISK BLOCKED: {symbol} -> {reason}")
            continue

        log_trade(
            symbol=symbol,
            entry_price=price,
            stop_distance=stop_distance,
            lot=lot
        )

        print(f"PRO TRADE AÇILDI: {symbol}")
        new_trades += 1

    await update.message.reply_text(f"✅ Scan tamamlandı.\nYeni açılan işlem: {new_trades}")

# ===============================
# BALANCE COMMAND
# ===============================

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    summary = get_balance_summary()

    message = (
        "📊 PORTFÖY DURUMU\n\n"
        f"Toplam Equity: {summary['equity']} TL\n"
        f"Toplam İşlem: {summary['total_trades']}\n"
        f"Açık Pozisyon: {summary['open_positions']}\n"
        f"Bağlanan Sermaye: {round(summary['used_capital'], 2)} TL"
    )

    await update.message.reply_text(message)

# ===============================
# MAIN
# ===============================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(CommandHandler("balance", balance))

    print("Institutional Portfolio Engine v2 başlatıldı...")

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
