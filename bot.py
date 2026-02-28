import os
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from performance_tracker import (
    log_trade,
    check_open_trades,
    get_portfolio_status
)

TOKEN = os.getenv("BOT_TOKEN")


# ==========================
# /scan
# ==========================

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("📊 Institutional Scan başlatıldı...")

    # Açık pozisyonları kontrol et
    check_open_trades()

    # Örnek dağılım (senin model çıktın buraya gelecek)
    trades = [
        {"symbol": "EREGL.IS", "lot": 641, "stop_distance": 1.56},
        {"symbol": "SISE.IS", "lot": 399, "stop_distance": 2.51},
        {"symbol": "KCHOL.IS", "lot": 88, "stop_distance": 11.41},
    ]

    for trade in trades:
        symbol = trade["symbol"]
        lot = trade["lot"]
        stop_distance = trade["stop_distance"]

        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")

            if hist.empty:
                print("PRICE DATA YOK:", symbol)
                continue

            price = float(hist["Close"].iloc[-1])

            log_trade(
                symbol=symbol,
                entry_price=price,
                stop_distance=float(stop_distance),
                lot=float(lot)
            )

            print("TRADE AÇILDI:", symbol)

        except Exception as e:
            print("TRADE LOG ERROR:", e)

    await update.message.reply_text("✅ Scan tamamlandı ve işlemler kaydedildi.")


# ==========================
# /balance
# ==========================

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    status = get_portfolio_status()

    message = (
        "📊 PORTFÖY DURUMU\n\n"
        f"Toplam Equity: {status['equity']} TL\n"
        f"Toplam İşlem: {status['total_trades']}\n"
        f"Açık Pozisyon: {status['open_positions']}"
    )

    await update.message.reply_text(message)


# ==========================
# MAIN
# ==========================

def main():
    print("Institutional Bot başlatıldı...")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(CommandHandler("balance", balance))

    app.run_polling()


if __name__ == "__main__":
    main()
