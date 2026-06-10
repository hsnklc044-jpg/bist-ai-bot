import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

from config import TELEGRAM_TOKEN

from core.indicator_engine import (
    analyze_stock
)

from core.support_engine import (
    get_support_resistance
)

from core.performance_report import (
    generate_report
)

from core.portfolio_report import (
    generate_portfolio_report
)

from core.top_signal import (
    get_top_signal
)

from core.market_report import (
    generate_market_report
)

from core.watchlist_report import (
    generate_watchlist
)

from core.daily_summary import (
    generate_daily_summary
)


# ==================================
# HELP
# ==================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    msg = (

        "📊 QUANT BIST AI\n\n"

        "/score EREGL\n"
        "/support EREGL\n"
        "/report\n"
        "/portfolio\n"
        "/top\n"
        "/market\n"
        "/watchlist\n"
        "/daily\n"
        "/help"
    )

    await update.message.reply_text(msg)


# ==================================
# SCORE
# ==================================

async def score_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        if len(context.args) == 0:

            await update.message.reply_text(
                "Kullanım:\n/score EREGL"
            )

            return

        symbol = (
            context.args[0].upper()
            + ".IS"
        )

        result = analyze_stock(symbol)

        if not result:

            await update.message.reply_text(
                "❌ Veri alınamadı"
            )

            return

        msg = (

            f"📊 {result['symbol']}\n\n"

            f"AI Score : {result['score']}\n"
            f"Signal : {result['signal']}\n"
            f"Trend : {result['trend']}\n\n"

            f"Confidence : {result['confidence']}%\n\n"

            f"RSI : {result['rsi']}\n"
            f"MACD : {result['macd']}\n"
            f"ATR : {result['atr']}\n\n"

            f"Entry : {result['entry_price']}\n"
            f"Stop : {result['stop_loss']}\n"

            f"Target 1 : {result['target_1']}\n"
            f"Target 2 : {result['target_2']}"
        )

        await update.message.reply_text(msg)

    except Exception as e:

        await update.message.reply_text(
            f"❌ Hata\n{e}"
        )


# ==================================
# SUPPORT
# ==================================

async def support_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        if len(context.args) == 0:

            await update.message.reply_text(
                "Kullanım:\n/support EREGL"
            )

            return

        symbol = (
            context.args[0].upper()
            + ".IS"
        )

        result = get_support_resistance(
            symbol
        )

        if not result:

            await update.message.reply_text(
                "❌ Veri alınamadı"
            )

            return

        msg = (

            f"📈 {result['symbol']}\n\n"

            f"Price : {result['price']}\n\n"

            f"Support 1 : {result['support_1']}\n"
            f"Support 2 : {result['support_2']}\n\n"

            f"Resistance 1 : {result['resistance_1']}\n"
            f"Resistance 2 : {result['resistance_2']}\n\n"

            f"Trend : {result['trend']}"
        )

        await update.message.reply_text(msg)

    except Exception as e:

        await update.message.reply_text(
            f"❌ Hata\n{e}"
        )


# ==================================
# REPORT
# ==================================

async def report_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        report = generate_report()

        await update.message.reply_text(
            report
        )

    except Exception as e:

        await update.message.reply_text(
            f"❌ Hata\n{e}"
        )


# ==================================
# PORTFOLIO
# ==================================

async def portfolio_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        report = generate_portfolio_report()

        await update.message.reply_text(
            report
        )

    except Exception as e:

        await update.message.reply_text(
            f"❌ Hata\n{e}"
        )


# ==================================
# TOP SIGNAL
# ==================================

async def top_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        report = get_top_signal()

        await update.message.reply_text(
            report
        )

    except Exception as e:

        await update.message.reply_text(
            f"❌ Hata\n{e}"
        )


# ==================================
# MARKET
# ==================================

async def market_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        report = generate_market_report()

        await update.message.reply_text(
            report
        )

    except Exception as e:

        await update.message.reply_text(
            f"❌ Hata\n{e}"
        )


# ==================================
# WATCHLIST
# ==================================

async def watchlist_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        report = generate_watchlist()

        await update.message.reply_text(
            report
        )

    except Exception as e:

        await update.message.reply_text(
            f"❌ Hata\n{e}"
        )
# ==================================
# DAILY SUMMARY
# ==================================

async def daily_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        report = generate_daily_summary()

        await update.message.reply_text(
            report
        )

    except Exception as e:

        await update.message.reply_text(
            f"❌ Hata\n{e}"
        )

# ==================================
# MAIN
# ==================================

def main():

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "help",
            help_command
        )
    )

    app.add_handler(
        CommandHandler(
            "score",
            score_command
        )
    )

    app.add_handler(
        CommandHandler(
            "support",
            support_command
        )
    )

    app.add_handler(
        CommandHandler(
            "report",
            report_command
        )
    )

    app.add_handler(
        CommandHandler(
            "portfolio",
            portfolio_command
        )
    )

    app.add_handler(
        CommandHandler(
            "top",
            top_command
        )
    )

    app.add_handler(
        CommandHandler(
            "market",
            market_command
        )
    )

    app.add_handler(
        CommandHandler(
            "watchlist",
            watchlist_command
        )
    )

    app.add_handler(
        CommandHandler(
            "daily",
            daily_command
        )
    )

    print(
        "✅ Quant BIST AI V2 Çalışıyor..."
    )

    app.run_polling()


if __name__ == "__main__":

    main()