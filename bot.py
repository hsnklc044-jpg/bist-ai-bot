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

# ===== STRATEGY SETTINGS =====
MAX_OPEN_POSITIONS = 5
RISK_PER_TRADE = 0.02        # %2 risk
MAX_POSITION_PCT = 0.20      # Max %20 per position
MAX_TOTAL_EXPOSURE = 1.0     # Max %100 exposure
ATR_PERIOD = 14


# ==========================
# START
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏦 Institutional Portfolio Engine v2 Aktif\n\n"
        "/scan → Yeni fırsat tara\n"
        "/balance → Portföy durumu\n"
    )


# ==========================
# SCAN
# ==========================

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("📊 Institutional Scan başlatıldı...")

    status = get_portfolio_status()
    equity = status["equity"]
    current_allocation = status["allocated_capital"]

    open_trades = check_open_trades()
    open_symbols = [t["symbol"] for t in open_trades]

    available_slots = MAX_OPEN_POSITIONS - len(open_trades)

    if available_slots <= 0:
        await update.message.reply_text("⚠️ Maksimum açık pozisyon limitine ulaşıldı.")
        return

    model_output = [
        {"symbol": "EREGL.IS", "score": 0.92},
        {"symbol": "SISE.IS", "score": 0.87},
        {"symbol": "KCHOL.IS", "score": 0.81},
        {"symbol": "THYAO.IS", "score": 0.76},
        {"symbol": "BIMAS.IS", "score": 0.72},
    ]

    model_output = sorted(model_output, key=lambda x: x["score"], reverse=True)

    new_trades = 0

    for item in model_output:

        if new_trades >= available_slots:
            break

        symbol = item["symbol"]

        if symbol in open_symbols:
            continue

        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="3mo")

            if hist.empty:
                continue

            price = float(hist["Close"].iloc[-1])

            # === ATR ===
            high_low = hist["High"] - hist["Low"]
            high_close = abs(hist["High"] - hist["Close"].shift())
            low_close = abs(hist["Low"] - hist["Close"].shift())

            tr = high_low.combine(high_close, max).combine(low_close, max)
            atr = tr.rolling(ATR_PERIOD).mean().iloc[-1]

            if atr is None or atr == 0:
                continue

            stop_distance = float(atr)

            # === Risk Based Lot ===
            risk_amount = equity * RISK_PER_TRADE
            lot = risk_amount / stop_distance

            # === Allocation hesapla ===
            allocation = lot * price

            # === Max %20 per position kontrol ===
            max_position_value = equity * MAX_POSITION_PCT
            if allocation > max_position_value:
                lot = max_position_value / price
                allocation = lot * price

            # === Max total exposure kontrol ===
            if (current_allocation + allocation) > (equity * MAX_TOTAL_EXPOSURE):
                remaining_capital = (equity * MAX_TOTAL_EXPOSURE) - current_allocation
                if remaining_capital <= 0:
                    break
                lot = remaining_capital / price
                allocation = lot * price

            if lot <= 0:
                continue

            log_trade(
                symbol=symbol,
                entry_price=price,
                stop_distance=stop_distance,
                lot=float(lot)
            )

            current_allocation += allocation
            new_trades += 1

            print("PRO TRADE AÇILDI:", symbol)

        except Exception as e:
            print("SCAN ERROR:", e)

    await update.message.reply_text(
        f"✅ Scan tamamlandı.\nYeni açılan işlem: {new_trades}"
    )


# ==========================
# BALANCE
# ==========================

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    status = get_portfolio_status()

    message = (
        "📊 PORTFÖY DURUMU\n\n"
        f"Toplam Equity: {status['equity']} TL\n"
        f"Toplam İşlem: {status['total_trades']}\n"
        f"Açık Pozisyon: {status['open_positions']}\n"
        f"Bağlanan Sermaye: {round(status['allocated_capital'],2)} TL"
    )

    await update.message.reply_text(message)


# ==========================
# MAIN
# ==========================

def main():

    print("Institutional Portfolio Engine v2 başlatıldı...")

    if not TOKEN:
        print("BOT_TOKEN bulunamadı!")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(CommandHandler("balance", balance))

    app.run_polling()


if __name__ == "__main__":
    main()
