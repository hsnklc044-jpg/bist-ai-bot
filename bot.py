import os
import logging
from datetime import datetime, date
from sqlalchemy import create_engine, text
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from risk_engine import risk_check_before_trade

# ==========================
# ENV VARIABLES
# ==========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN missing")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL missing")

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

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# ==========================
# DATABASE HELPERS
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

    return float(equity or 0), int(total_trades or 0), int(open_positions or 0)


# ==========================
# TELEGRAM COMMANDS
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Institutional Portfolio Engine v2 aktif."
    )


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


# ==========================

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("🔎 Institutional Scan başlatıldı...")

    allowed, reason = risk_check_before_trade()

    if not allowed:
        await update.message.reply_text(f"🛑 Trade Engellendi: {reason}")
        return

    # ÖRNEK TRADE INSERT
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO trades (symbol, status, open_time, pnl)
            VALUES ('EREGL.IS', 'OPEN', :open_time, 0)
        """), {"open_time": datetime.utcnow()})

    await update.message.reply_text("✅ Yeni işlem açıldı.")


# ==========================

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):

    with engine.connect() as conn:

        equity = conn.execute(
            text("SELECT equity FROM portfolio ORDER BY id DESC LIMIT 1")
        ).scalar()

        total_pnl = conn.execute(
            text("SELECT COALESCE(SUM(pnl),0) FROM trades")
        ).scalar()

        daily_pnl = conn.execute(
            text("""
                SELECT COALESCE(SUM(pnl),0)
                FROM trades
                WHERE DATE(open_time) = :today
            """),
            {"today": date.today()}
        ).scalar()

        open_positions = conn.execute(
            text("SELECT COUNT(*) FROM trades WHERE status='OPEN'")
        ).scalar()

    equity = float(equity or 0)
    total_pnl = float(total_pnl or 0)
    daily_pnl = float(daily_pnl or 0)
    open_positions = int(open_positions or 0)

    # Risk hesapları
    daily_loss_limit = equity * 0.02
    risk_status = "🟢 Normal"

    if daily_pnl <= -daily_loss_limit:
        risk_status = "🔴 Daily Max Loss Aktif"

    baseline = 100000
    profit_lock = "🔓 Kapalı"

    if equity >= baseline * 1.10:
        profit_lock = "🔐 Aktif"

    message = (
        "📊 KURUMSAL RAPOR\n\n"
        f"💰 Equity: {equity:.2f} TL\n"
        f"📈 Toplam PnL: {total_pnl:.2f} TL\n"
        f"📅 Günlük PnL: {daily_pnl:.2f} TL\n"
        f"📦 Açık Pozisyon: {open_positions}\n\n"
        f"🛑 Günlük Risk Limiti: {risk_status}\n"
        f"🔐 Profit Lock: {profit_lock}"
    )

    await update.message.reply_text(message)


# ==========================
# MAIN
# ==========================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(CommandHandler("report", report))

    logger.info("Institutional Portfolio Engine v2 başlatıldı...")
    app.run_polling()


if __name__ == "__main__":
    main()
