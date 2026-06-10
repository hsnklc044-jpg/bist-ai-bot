from core.support_engine import get_support_resistance
from core.indicator_engine import analyze_stock
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from core.performance_report import generate_performance_report
from core.portfolio_report import generate_portfolio_report

BOT_TOKEN = "8434925197:AAHeciNObLAkLJ_SE_jsaNPvhiwR9_HRoTE"


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🤖 QuantBIST AI Ready\n\n"
        "/start\n"
        "/performance\n"
        "/portfolio"
    )


async def performance(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        generate_performance_report()
    )


async def portfolio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        generate_portfolio_report()
    )


app = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .build()
)

app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app.add_handler(
    CommandHandler(
        "performance",
        performance
    )
)

app.add_handler(
    CommandHandler(
        "portfolio",
        portfolio
    )
)

print(
    "🚀 Telegram Command Bot Started"
)

app.run_polling(
    drop_pending_updates=True
)