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
            target FLOAT,
            pnl FLOAT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    await update.message.reply_text("BIST AI Performance Engine aktif 🚀")

# 🔥 ADDTRADE + PNL HESABI
async def addtrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip()
        parts = text.split()

        if len(parts) != 5:
            await update.message.reply_text(
                "❌ Hatalı kullanım.\nÖrnek:\n/addtrade EREGL long 42 45"
            )
            return

        _, symbol, side, entry, target = parts

        entry = float(entry)
        target = float(target)

        # PNL hesap
        if side.lower() == "long":
            pnl = target - entry
        else:
            pnl = entry - target

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO trades (symbol, side, entry, target, pnl) VALUES (%s, %s, %s, %s, %s)",
            (symbol.upper(), side.lower(), entry, target, pnl)
        )

        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(f"✅ Trade kaydedildi. PnL: {round(pnl,2)}")

    except Exception as e:
        logger.error(f"ADDTRADE ERROR: {e}")
        await update.message.reply_text("❌ Sistem hatası.")

# 🔥 PROFESYONEL EQUITY
async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT pnl FROM trades;")
        rows = cur.fetchall()

        if not rows:
            await update.message.reply_text("Henüz trade yok.")
            return

        pnls = [r[0] for r in rows]

        total_trades = len(pnls)
        wins = len([p for p in pnls if p > 0])
        losses = len([p for p in pnls if p < 0])

        win_rate = round((wins / total_trades) * 100, 2) if total_trades > 0 else 0
        net_pnl = round(sum(pnls), 2)

        avg_win = round(sum([p for p in pnls if p > 0]) / wins, 2) if wins > 0 else 0
        avg_loss = round(sum([p for p in pnls if p < 0]) / losses, 2) if losses > 0 else 0

        rr = round(abs(avg_win / avg_loss), 2) if avg_loss != 0 else 0

        msg = f"""
📊 TRADE PERFORMANS

Toplam Trade: {total_trades}
Kazanan: {wins}
Kaybeden: {losses}
Win Rate: %{win_rate}

💰 Net PnL: {net_pnl}
📈 Ortalama Kazanç: {avg_win}
📉 Ortalama Zarar: {avg_loss}
⚖️ Risk/Reward: {rr}
"""

        await update.message.reply_text(msg)

        cur.close()
        conn.close()

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

    # Conflict önleyici
    application.run_polling(drop_pending_updates=True)

# -------------------------

if __name__ == "__main__":
    main()
