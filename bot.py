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
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# -------------------------
# ENV VARIABLES
# -------------------------
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DATABASE_URL = os.getenv("DATABASE_URL")

print("TOKEN DEBUG:", TOKEN)

# -------------------------
# DATABASE INIT
# -------------------------
def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id SERIAL PRIMARY KEY,
                symbol TEXT,
                direction TEXT,
                entry FLOAT,
                exit FLOAT,
                profit FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        cur.close()
        conn.close()

        print("DB INIT SUCCESS")

    except Exception as e:
        print("DB INIT ERROR:", e)


# -------------------------
# COMMANDS
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("BIST AI Bot aktif 🚀")


async def addtrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args

        symbol = args[0]
        direction = args[1]
        entry = float(args[2])
        exit_price = float(args[3])

        if direction.lower() == "long":
            profit = exit_price - entry
        else:
            profit = entry - exit_price

        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO trades (symbol, direction, entry, exit, profit)
            VALUES (%s, %s, %s, %s, %s)
        """, (symbol, direction, entry, exit_price, profit))

        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(f"Trade eklendi ✅ Profit: {round(profit,2)}")

    except Exception as e:
        logger.error(f"Addtrade error: {e}")
        await update.message.reply_text("❌ Hatalı kullanım.\nÖrnek:\n/addtrade EREGL long 42 45")


async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("SELECT profit FROM trades ORDER BY id ASC")
        rows = cur.fetchall()

        conn.close()

        equity = 0
        curve = []

        for row in rows:
            equity += row[0]
            curve.append(equity)

        if not curve:
            await update.message.reply_text("Henüz trade yok.")
            return

        final_equity = round(curve[-1], 2)

        await update.message.reply_text(f"📈 Güncel Equity: {final_equity}")

    except Exception as e:
        logger.error(f"Equity error: {e}")
        await update.message.reply_text("❌ Equity hesaplanamadı.")


# -------------------------
# MAIN
# -------------------------
def main():
    if not TOKEN:
        print("TOKEN BULUNAMADI!")
        return

    init_db()

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addtrade", addtrade))
    application.add_handler(CommandHandler("equity", equity))

    application.run_polling()


if __name__ == "__main__":
    main()
