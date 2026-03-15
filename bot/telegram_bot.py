import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

from support_engine import get_support_resistance
from radar_engine import run_radar
from ultra_radar_engine import run_ultra_radar
from ai_engine import get_ai_score
from decision_engine import get_trade_decision
from setup_engine import generate_trade_setups
from journal_engine import save_trade, get_journal
from performance_engine import analyze_performance
from auto_radar import auto_scan


TOKEN = "8772282578:AAHayduiZtDuf659L0Fx9H8ehOcn81tii10"


# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = (
        "🤖 BIST AI Bot Aktif!\n\n"
        "Komutlar:\n\n"
        "/support EREGL\n"
        "/radar\n"
        "/ultra\n"
        "/ai THYAO\n"
        "/decision THYAO\n"
        "/setup\n"
        "/journal\n"
        "/performance\n"
        "/autoradar\n"
        "/status"
    )

    await update.message.reply_text(message)


# STATUS
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("✅ Bot çalışıyor")


# SUPPORT
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Kullanım: /support EREGL")
        return

    symbol = context.args[0].upper()

    support, resistance = get_support_resistance(symbol)

    if support is None:
        await update.message.reply_text("Veri alınamadı")
        return

    message = (
        f"📊 {symbol} Analiz\n\n"
        f"Destek → {support}\n"
        f"Direnç → {resistance}"
    )

    await update.message.reply_text(message)


# RADAR
async def radar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    results = run_radar()

    if not results:
        await update.message.reply_text("Radar sonucu bulunamadı")
        return

    message = "📊 BIST RADAR\n\n"

    for i, (symbol, score) in enumerate(results, 1):

        message += f"{i}. {symbol} → Score {score}\n"

    await update.message.reply_text(message)


# ULTRA RADAR
async def ultra(update: Update, context: ContextTypes.DEFAULT_TYPE):

    results = run_ultra_radar()

    if not results:
        await update.message.reply_text("Ultra radar sonucu bulunamadı")
        return

    message = "⚡ ULTRA RADAR\n\n"

    for i, (symbol, score) in enumerate(results, 1):

        message += f"{i}. {symbol} → Score {score}\n"

    await update.message.reply_text(message)


# AI SCORE
async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Kullanım: /ai THYAO")
        return

    symbol = context.args[0].upper()

    score = get_ai_score(symbol)

    if score is None:
        await update.message.reply_text("AI veri alınamadı")
        return

    await update.message.reply_text(
        f"🤖 {symbol}\n\nAI Score → {score}"
    )


# DECISION
async def decision(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Kullanım: /decision THYAO")
        return

    symbol = context.args[0].upper()

    data = get_trade_decision(symbol)

    if data is None:
        await update.message.reply_text("Veri alınamadı")
        return

    message = (
        "🤖 AI TRADE DECISION\n\n"
        f"{data['symbol']}\n"
        f"Score → {data['score']}\n\n"
        f"Trend → {data['trend']}\n"
        f"Momentum → {data['momentum']}\n"
        f"Volume → {data['volume']}\n\n"
        f"Action → {data['action']}\n"
        f"Confidence → {data['confidence']}"
    )

    await update.message.reply_text(message)


# TRADE SETUP
async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE):

    setups = generate_trade_setups()

    if not setups:
        await update.message.reply_text("Setup bulunamadı")
        return

    message = "🚨 AI TRADE SETUPS\n\n"

    for s in setups:

        save_trade(s)

        message += (
            f"{s['symbol']}\n"
            f"Entry → {s['entry']}\n"
            f"Target → {s['target']}\n"
            f"Stop → {s['stop']}\n"
            f"Confidence → {s['confidence']}%\n\n"
        )

    await update.message.reply_text(message)


# JOURNAL
async def journal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    trades = get_journal()

    if not trades:
        await update.message.reply_text("Trade journal boş")
        return

    message = "📒 TRADE JOURNAL\n\n"

    for t in trades[-10:]:

        message += (
            f"{t['symbol']}\n"
            f"Entry → {t['entry']}\n"
            f"Target → {t['target']}\n"
            f"Stop → {t['stop']}\n"
            f"Confidence → {t['confidence']}%\n"
            f"Date → {t['date']}\n\n"
        )

    await update.message.reply_text(message)


# PERFORMANCE
async def performance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = analyze_performance()

    if data is None:
        await update.message.reply_text("Performans verisi yok")
        return

    message = (
        "📊 PERFORMANCE REPORT\n\n"
        f"Trades → {data['trades']}\n"
        f"Win Rate → {data['win_rate']}%\n"
        f"Avg Confidence → {data['avg_conf']}%"
    )

    await update.message.reply_text(message)


# AUTO ALERT
async def auto_alert(context: ContextTypes.DEFAULT_TYPE):

    alerts = auto_scan()

    if not alerts:
        return

    for a in alerts:

        message = (
            "🚨 AUTO RADAR ALERT\n\n"
            f"{a['symbol']}\n"
            f"AI Score → {a['score']}"
        )

        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=message
        )


# AUTORADAR
async def autoradar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.job_queue.run_repeating(
        auto_alert,
        interval=300,
        first=10,
        chat_id=update.effective_chat.id
    )

    await update.message.reply_text(
        "⚡ Auto Radar başlatıldı (5 dk tarama)"
    )


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("radar", radar))
    app.add_handler(CommandHandler("ultra", ultra))
    app.add_handler(CommandHandler("ai", ai))
    app.add_handler(CommandHandler("decision", decision))
    app.add_handler(CommandHandler("setup", setup))
    app.add_handler(CommandHandler("journal", journal))
    app.add_handler(CommandHandler("performance", performance))
    app.add_handler(CommandHandler("autoradar", autoradar))

    print("🚀 Telegram bot başlatıldı")

    app.run_polling()


if __name__ == "__main__":
    main()
