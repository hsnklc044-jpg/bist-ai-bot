import os
import logging
import psycopg2
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# -------------------------
# LOGGING
# -------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------------------------
# ENV VARIABLES
# -------------------------

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# -------------------------
# DATABASE CONNECTION
# -------------------------

def get_connection():
    url = urlparse(DATABASE_URL)

    return psycopg2.connect(
        host=url.hostname,
        port=url.port,
        user=url.username,
        password=url.password,
        dbname=url.path[1:]
    )

def init_db():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            symbol TEXT,
            side TEXT,
            entry FLOAT,
            target FLOAT
        );
        """)

        conn.commit()
        cur.close()
        conn.close()
        logger.info("DB INIT SUCCESS")

    except Exception as e:
        logger.error(f"DB INIT ERROR: {e}")

# -------------------------
# COMMANDS
# -------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("BIST AI Bot aktif 🚀")

async def addtrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = context.args[0]
        side = context.args[1]
        entry = float(context.args[2])
        target = float(context.args[3])

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO trades (symbol, side, entry, target) VALUES (%s, %s, %s, %s)",
            (symbol, side, entry, target)
        )

        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text("✅ Trade kaydedildi.")

    except Exception as e:
        logger.error(f"ADDTRADE ERROR: {e}")
        await update.message.reply_text(
            "❌ Hatalı kullanım.\nÖrnek:\n/addtrade EREGL long 42 45"
        )

async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT entry, target FROM trades")
        rows = cur.fetchall()

        if not rows:
            await update.message.reply_text("Henüz trade yok.")
            return

        equity = 0
        for entry, target in rows:
            equity += (target - entry)

        cur.close()
        conn.close()

        await update.message.reply_text(f"📈 Güncel Equity: {round(equity, 2)}")

    except Exception as e:
        logger.error(f"EQUITY ERROR: {e}")
        await update.message.reply_text("❌ Equity hesaplanamadı.")

# -------------------------
# MAIN
# -------------------------

def main():
    if not TOKEN:
        logger.error("TELEGRAM_TOKEN bulunamadı.")
        return

    if not DATABASE_URL:
        logger.error("DATABASE_URL bulunamadı.")
        return

    init_db()

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addtrade", addtrade))
    application.add_handler(CommandHandler("equity", equity))

    # 🔥 Conflict çözümü burada
    application.run_polling(
        drop_pending_updates=True
    )

# -------------------------

if __name__ == "__main__":
    main()
