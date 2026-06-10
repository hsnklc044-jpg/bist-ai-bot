from core.summary_report import (
    generate_summary_report
)
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from core.performance_report import generate_performance_report
from core.portfolio_report import generate_portfolio_report
from core.support_engine import get_support_resistance
from core.indicator_engine import analyze_stock
from core.top_signals import get_top_signals
from core.trade_journal import generate_trade_journal
from core.backtest_engine import run_backtest
from core.risk_manager import calculate_position_size
from core.ai_report import generate_ai_report
from core.portfolio_allocator_v4 import allocate_portfolio_v4
from core.live_portfolio_builder import build_live_portfolio
from core.rebalancing_engine_v3 import generate_rebalance_report_v3
from core.ai_report import generate_ai_report

from core.pdf_report import (
    generate_pdf_report
)

from core.telegram_daily_report import (
    generate_telegram_daily_report
)

from core.portfolio_health import (
    generate_portfolio_health
)

from core.market_scan import (
    generate_market_scan
)

from core.performance_metrics import (
    generate_performance_metrics
)

from core.alert_engine import (
    generate_alerts
)

from core.morning_report import (
    generate_morning_report
)

from config import BOT_TOKEN


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 QuantBIST AI Ready\n\n"
        "/start\n"
        "/performance\n"
        "/portfolio\n"
        "/support EREGL\n"
        "/analyze EREGL\n"
        "/top\n"
        "/journal\n"
        "/backtest EREGL\n"
        "/position 100000 1 39 36\n"
        "/allocate 100000\n"
        "/buildportfolio 100000\n"
        "/rebalance\n"
        "/daily\n"
        "/health\n"
        "/scan\n"
        "/metrics\n"
        "/alerts\n"
        "/morning"
        "\n/summary"
        "/pdf"
        "/ai"
        "/ai\n"
    )


async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        generate_ai_report()
    )

async def performance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        generate_performance_report()
    )


async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        generate_portfolio_report()
    )

async def ai(update, context):

    await update.message.reply_text(
        generate_ai_report()
    )


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) == 0:

        await update.message.reply_text(
            "Kullanim:\n/support EREGL"
        )

        return

    symbol = (
        context.args[0].upper().replace(".IS", "")
        + ".IS"
    )

    data = get_support_resistance(symbol)

    if not data:

        await update.message.reply_text(
            "Veri bulunamadi."
        )

        return

    message = (
        f"📊 {data['symbol']}\n\n"
        f"💰 Price : {data['price']}\n\n"
        f"🟢 SUPPORTS\n\n"
        f"S1 : {data['support_1']}\n"
        f"S2 : {data['support_2']}\n\n"
        f"🔴 RESISTANCES\n\n"
        f"R1 : {data['resistance_1']}\n"
        f"R2 : {data['resistance_2']}\n\n"
        f"📈 Trend : {data['trend']}"
    )

    await update.message.reply_text(message)


async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) == 0:

        await update.message.reply_text(
            "Kullanim:\n/analyze EREGL"
        )

        return

    symbol = (
        context.args[0].upper().replace(".IS", "")
        + ".IS"
    )

    data = analyze_stock(symbol)

    if not data:

        await update.message.reply_text(
            "Analiz uretilemedi."
        )

        return

    message = (
        f"📊 {data['symbol']} ANALYSIS\n\n"
        f"🎯 Signal : {data['signal']}\n"
        f"🔥 Score : {data['score']}/100\n"
        f"⭐ Confidence : {data['confidence']}%\n\n"
        f"📈 Trend : {data['trend']}\n"
        f"📉 RSI : {data['rsi']}\n"
        f"⚡ MACD : {data['macd']}\n\n"
        f"💰 Entry : {data['entry_price']}\n"
        f"🛑 Stop Loss : {data['stop_loss']}\n"
        f"🎯 Target 1 : {data['target_1']}\n"
        f"🎯 Target 2 : {data['target_2']}"
    )

    await update.message.reply_text(message)


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):

    signals = get_top_signals()

    if not signals:

        await update.message.reply_text(
            "No signal found."
        )

        return

    message = "🔥 TOP AI SIGNALS\n\n"

    for i, s in enumerate(signals, start=1):

        message += (
            f"{i}. {s['symbol']}\n"
            f"Score : {s['score']}\n"
            f"Signal : {s['signal']}\n"
            f"Trend : {s['trend']}\n\n"
        )

    await update.message.reply_text(message)


async def journal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        generate_trade_journal()
    )


async def backtest(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) == 0:

        await update.message.reply_text(
            "Kullanim:\n/backtest EREGL"
        )

        return

    symbol = (
        context.args[0].upper().replace(".IS", "")
        + ".IS"
    )

    await update.message.reply_text(
        run_backtest(symbol)
    )


async def position(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) != 4:

        await update.message.reply_text(
            "Kullanim:\n/position 100000 1 39 36"
        )

        return

    result = calculate_position_size(
        float(context.args[0]),
        float(context.args[1]),
        float(context.args[2]),
        float(context.args[3])
    )

    await update.message.reply_text(result)


async def allocate(update: Update, context: ContextTypes.DEFAULT_TYPE):

    capital = 100000

    if len(context.args) == 1:
        capital = float(context.args[0])

    await update.message.reply_text(
        allocate_portfolio_v4(capital)
    )


async def buildportfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):

    capital = 100000

    if len(context.args) == 1:
        capital = float(context.args[0])

    await update.message.reply_text(
        build_live_portfolio(capital)
    )


async def rebalance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        generate_rebalance_report_v3()
    )


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        generate_telegram_daily_report()
    )


async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        generate_portfolio_health()
    )


async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        generate_market_scan()
    )


async def metrics(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        generate_performance_metrics()
    )


async def alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        generate_alerts()
    )

async def morning(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        generate_morning_report()
    )
async def pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):

    filename = generate_pdf_report()

    with open(filename, "rb") as pdf_file:

        await update.message.reply_document(
            document=pdf_file,
            filename=filename
    )

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        generate_summary_report()
    )

app = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .connect_timeout(60)
    .read_timeout(60)
    .write_timeout(60)
    .pool_timeout(60)
    .build()
)
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("performance", performance))
app.add_handler(CommandHandler("portfolio", portfolio))
app.add_handler(CommandHandler("support", support))
app.add_handler(CommandHandler("analyze", analyze))
app.add_handler(CommandHandler("top", top))
app.add_handler(CommandHandler("journal", journal))
app.add_handler(CommandHandler("backtest", backtest))
app.add_handler(CommandHandler("position", position))
app.add_handler(CommandHandler("allocate", allocate))
app.add_handler(CommandHandler("buildportfolio", buildportfolio))
app.add_handler(CommandHandler("rebalance", rebalance))
app.add_handler(CommandHandler("daily", daily))
app.add_handler(CommandHandler("health", health))
app.add_handler(CommandHandler("scan", scan))
app.add_handler(CommandHandler("metrics", metrics))
app.add_handler(CommandHandler("alerts", alerts))
app.add_handler(CommandHandler("morning", morning))
app.add_handler(CommandHandler("ai", ai))
app.add_handler(
    CommandHandler("pdf", pdf)
)
app.add_handler(
    CommandHandler(
        "summary",
        summary
    )
)
async def ai(update, context):

    await update.message.reply_text(
        generate_ai_report()
    )

print("🚀 QuantBIST AI Started")

app.run_polling(
    drop_pending_updates=True,
    timeout=60
)