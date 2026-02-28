import os
import logging
import asyncio
from datetime import datetime
from sqlalchemy import create_engine, text
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from risk_engine import risk_check_before_trade

# ==========================
# ENV VARIABLES
# ==========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DATABASE_URL = os.getenv("DATABASE_URL")

# ==========================
# LOGGING
# ==========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ==========================
# DATABASE
# ==========================

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ==========================
# PORTFOLIO FUNCTIONS
# ==========================

def get_portfolio_status():
    with engine.connect() as conn:
        equity = conn.execute(
            text("SELECT equity FROM portfolio ORDER BY id DESC LIMIT 1")
        ).scalar()

        total_trades = conn.execute(
            text("SELECT COUNT(*) FROM trades")
        ).scalar()

        open_positions = conn.execute(
            text("SELECT COUNT(*) FROM trades WHERE status='OPEN'")
        ).scalar()

    return equity, total_trades, open_positions


# ==========================
# TELEGRAM COMMANDS
# ==========================

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    equity, total_trades, open_positions = get_portfolio_status()

    message = (
        "📊 PORTFÖY DURUMU\n\n"
        f"Toplam Equity: {equity:.2f} TL\n"
        f"Toplam İşlem: {total_trades}\n"
        f"Açık Pozisyon: {open_positions}\n"
        f"Bağlanan Sermaye: {equity:.2f} TL"
    )

    await update.message.reply_text(message)


async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("🔎 Institutional Scan başlatıldı...")

    allowed, reason = risk_check_before_trade()

    if not allowed:
        await update.message.reply_text(f"🛑 Trade Engellendi: {reason}")
        return

    # ÖRNEK TRADE SİMÜLASYONU
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO trades (symbol, status, open_time, pnl)
            VALUES ('EREGL.IS', 'OPEN', :open_time, 0)
        """), {"open_time": datetime.utcnow()})

    await update.message.reply_text("✅ Yeni işlem açıldı.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Institutional Portfolio Engine v2 aktif.")


# ==========================
# MAIN
# ==========================

def main():

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN missing")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("scan", scan))

    logger.info("Institutional Portfolio Engine v2 başlatıldı...")
    app.run_polling()


if __name__ == "__main__":
    main()
