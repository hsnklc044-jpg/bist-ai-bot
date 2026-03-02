import os
import logging
import psycopg2
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# -------------------------
# ENV VARIABLES
# -------------------------

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DATABASE_URL = os.getenv("DATABASE_URL")

# -------------------------
# LOGGING
# -------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# -------------------------
# DATABASE CONNECTION
# -------------------------

def get_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not found!")

    url = urlparse(DATABASE_URL)

    conn = psycopg2.connect(
        host=url.hostname,
        database=url.path[1:],
        user=url.username,
        password=url.password,
        port=url.port
    )
    return conn


def init_db():
    print("INIT_DB STARTING...")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            symbol TEXT,
            direction TEXT,
            entry FLOAT,
            exit FLOAT,
            r_multiple FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

    print("INIT_DB SUCCESS")


def add_trade_db(symbol, direction, entry, exit_price):
    r_multiple = (exit_price - entry) / entry if direction == "long" else (entry - exit_price) / entry

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO trades (symbol, direction, entry, exit, r_multiple)
        VALUES (%s, %s, %s, %s, %s)
    """, (symbol, direction, entry, exit_price, r_multiple))

    conn.commit()
    cur.close()
    conn.close()


def get_equity_curve():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT r_multiple FROM trades ORDER BY id ASC")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    equity = 1.0
    curve = [equity]

    for r in rows:
        equity *= (1 + r[0])
        curve.append(equity)

    return curve


# -------------------------
# COMMANDS
# -------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("BIST AI Bot aktif 🚀")


async def addtrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args

        if len(args) != 4:
            await update.message.reply_text(
                "Kullanım:\n/addtrade SYMBOL long/short entry exit"
            )
            return

        symbol = args[0]
        direction = args[1]
        entry = float(args[2])
        exit_price = float(args[3])

        add_trade_db(symbol, direction, entry, exit_price)

        await update.message.reply_text("✅ Trade kaydedildi.")

    except Exception as e:
        logger.error(f"Addtrade error: {e}")
        await update.message.reply_text("❌ Trade kaydedilemedi.")


async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        curve = get_equity_curve()

        if len(curve) <= 1:
            await update.message.reply_text("Henüz yeterli trade yok.")
            return

        final_equity = round(curve[-1], 3)

        await update.message.reply_text(
            f"📈 Güncel Equity: {final_equity}"
        )

    except Exception as e:
        logger.error(f"Equity error: {e}")
        await update.message.reply_text("❌ Equity hesaplanamadı.")


# -------------------------
# MAIN
# -------------------------

def main():
    try:
        init_db()
    except Exception as e:
        print("INIT_DB ERROR:", e)

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addtrade", addtrade))
    application.add_handler(CommandHandler("equity", equity))

    application.run_polling()


if __name__ == "__main__":
    main()
