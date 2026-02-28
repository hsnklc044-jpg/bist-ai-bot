import os
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from institutional_engine import scan_trades
from performance_tracker import (
    log_trade,
    get_balance,
    check_open_trades
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

    # 🔥 Açık trade kontrolü
    check_open_trades()

    await update.message.reply_text("📊 Institutional Scan başlatıldı...")

    try:
        result = scan_trades()

        if not result:
            await update.message.reply_text("Engine cevap vermedi.")
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

                print("DEBUG TRADE:", t)

                symbol = t.get("symbol")
                lot = t.get("lot")
                stop_distance = t.get("stop_distance")

                message += (
                    f"{symbol}\n"
                    f"Ağırlık: %{t.get('weight_%',0)}\n"
                    f"Lot: {lot}\n"
                    f"Tutar: {t.get('allocation',0)} TL\n\n"
                )

                # 🔥 Stop mesafesi kontrolü
                if stop_distance is None:
                    print("STOP DISTANCE YOK:", symbol)
                    continue

                try:
                    price_data = yf.download(symbol, period="1d", auto_adjust=True)

                    if price_data is None or price_data.empty:
                        print("PRICE DATA YOK:", symbol)
                        continue

                    price = price_data["Close"].iloc[-1]

                    log_trade(
                        symbol=symbol,
                        entry_price=float(price),
                        stop_distance=float(stop_distance),
                        lot=float(lot)
                    )

                    print("TRADE AÇILDI:", symbol)

                except Exception as e:
                    print("TRADE LOG ERROR:", e)

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"❌ SCAN HATA: {str(e)}")
        print("SCAN ERROR:", e)


# ================= BALANCE =================
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        balance_data = get_balance()

        message = (
            "📊 PORTFÖY DURUMU\n\n"
            f"Toplam Equity: {balance_data.get('equity',0)} TL\n"
            f"Toplam İşlem: {balance_data.get('total_trades',0)}\n"
            f"Açık Pozisyon: {balance_data.get('open_trades',0)}\n"
        )

        await update.message.reply_text(message)

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
