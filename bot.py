import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from config import TOKEN
from indicators import get_stock_data
from bist_symbols import BIST_SYMBOLS
from signal_engine import generate_signal
from scanner_ai import scan_market
from market_analyzer import analyze_market
from breakout_scanner import scan_breakouts
from auto_signal_scheduler import auto_signal_loop
from ai_trade_brain import ai_trade_signal


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    if "subscribers" not in context.application.bot_data:
        context.application.bot_data["subscribers"] = set()

    context.application.bot_data["subscribers"].add(chat_id)

    text = """
📊 BIST AI BOT

Komutlar:

/price HISSE
/support HISSE
/resistance HISSE
/scan
/signal HISSE
/scan_ai
/market
/breakout
/ai_signal

🔔 Otomatik sinyal sistemi aktif.
"""

    await update.message.reply_text(text)


# PRICE
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) == 0:
        await update.message.reply_text("Örnek kullanım:\n/price EREGL")
        return

    symbol = context.args[0]

    data = get_stock_data(symbol)

    if data is None:
        await update.message.reply_text("Hisse bulunamadı")
        return

    price, support, resistance = data

    msg = f"""
📈 {symbol}

Fiyat: {price:.2f} TL
Destek: {support:.2f}
Direnç: {resistance:.2f}
"""

    await update.message.reply_text(msg)


# SUPPORT
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) == 0:
        await update.message.reply_text("Örnek kullanım:\n/support EREGL")
        return

    symbol = context.args[0]

    data = get_stock_data(symbol)

    if data is None:
        await update.message.reply_text("Hisse bulunamadı")
        return

    price, support_level, resistance = data

    msg = f"""
📊 {symbol}

Güncel fiyat: {price:.2f}
Destek seviyesi: {support_level:.2f}
"""

    await update.message.reply_text(msg)


# RESISTANCE
async def resistance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) == 0:
        await update.message.reply_text("Örnek kullanım:\n/resistance EREGL")
        return

    symbol = context.args[0]

    data = get_stock_data(symbol)

    if data is None:
        await update.message.reply_text("Hisse bulunamadı")
        return

    price, support, resistance_level = data

    msg = f"""
📊 {symbol}

Güncel fiyat: {price:.2f}
Direnç seviyesi: {resistance_level:.2f}
"""

    await update.message.reply_text(msg)


# SCAN
async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    results = []

    for symbol in BIST_SYMBOLS:

        data = get_stock_data(symbol)

        if data is None:
            continue

        price, support, resistance = data

        if price <= support * 1.03:
            results.append(f"{symbol} ({price:.2f})")

    if not results:
        await update.message.reply_text("Fırsat hisse bulunamadı")
    else:
        msg = "📊 Destek yakın hisseler\n\n"
        msg += "\n".join(results)
        await update.message.reply_text(msg)


# SIGNAL
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) == 0:
        await update.message.reply_text("Örnek kullanım:\n/signal EREGL")
        return

    symbol = context.args[0]

    data = generate_signal(symbol)

    if data is None:
        await update.message.reply_text("Hisse bulunamadı")
        return

    price, support, resistance, rsi, score = data

    signal_text = "NEUTRAL"
    if score >= 70:
        signal_text = "BUY SIGNAL"

    msg = f"""
📊 {symbol}

Fiyat: {price:.2f}
RSI: {rsi:.2f}

Destek: {support:.2f}
Direnç: {resistance:.2f}

AI SCORE: {score}%

{signal_text}
"""

    await update.message.reply_text(msg)


# SCAN AI
async def scan_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("BIST taranıyor...")

    results = scan_market()

    if not results:
        await update.message.reply_text("Fırsat hisse bulunamadı")
        return

    msg = "🔥 AI FIRSAT HİSSELER\n\n"
    msg += "\n".join(results[:10])

    await update.message.reply_text(msg)


# MARKET
async def market(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("Piyasa analiz ediliyor...")

    rising, falling, avg_rsi, strong = analyze_market()

    msg = f"""
📊 BIST MARKET ANALİZİ

Yükselen hisseler: {rising}
Düşen hisseler: {falling}

Ortalama RSI: {avg_rsi:.2f}

🔥 Güçlü hisseler:
"""

    msg += "\n".join(strong)

    await update.message.reply_text(msg)


# BREAKOUT
async def breakout(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("Breakout hisseler aranıyor...")

    results = scan_breakouts()

    if not results:
        await update.message.reply_text("Breakout bulunamadı")
        return

    msg = "🚀 BREAKOUT HİSSELER\n\n"
    msg += "\n".join(results)

    await update.message.reply_text(msg)


# AI SIGNAL
async def ai_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) == 0:
        await update.message.reply_text("Örnek:\n/ai_signal EREGL")
        return

    symbol = context.args[0]

    data = ai_trade_signal(symbol)

    if data is None:
        await update.message.reply_text("Hisse bulunamadı")
        return

    price, support, resistance, rsi, score = data

    signal = "NEUTRAL"
    if score >= 80:
        signal = "🚀 STRONG BUY"
    elif score >= 60:
        signal = "📈 BUY SETUP"

    msg = f"""
🧠 AI TRADE ANALİZİ

{symbol}

Fiyat: {price:.2f}
RSI: {rsi:.2f}

Destek: {support:.2f}
Direnç: {resistance:.2f}

AI SCORE: {score}%

{signal}
"""

    await update.message.reply_text(msg)


# SCHEDULER
async def start_scheduler(app):
    asyncio.create_task(auto_signal_loop(app))


# MAIN
def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("resistance", resistance))
    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("scan_ai", scan_ai))
    app.add_handler(CommandHandler("market", market))
    app.add_handler(CommandHandler("breakout", breakout))
    app.add_handler(CommandHandler("ai_signal", ai_signal))

    app.post_init = start_scheduler

    print("Bot çalışıyor...")

    app.run_polling()


if __name__ == "__main__":
    main()