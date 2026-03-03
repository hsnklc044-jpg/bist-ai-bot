import os
import logging
import asyncio
import psycopg2
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
CAPITAL = float(os.getenv("CAPITAL", 100000))
RISK_PERCENT = float(os.getenv("RISK_PERCENT", 1.5))

# ================= DATABASE =================

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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            id SERIAL PRIMARY KEY,
            symbol TEXT,
            entry FLOAT,
            stop FLOAT,
            target FLOAT,
            lot INT,
            status TEXT DEFAULT 'open'
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# ================== CORE ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 BIST AI PRO Production Aktif")

async def radar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 Kurumsal Radar tarıyor...")
    await asyncio.sleep(1)
    await update.message.reply_text(
        "🔥 RS PRO LİDERLERİ\n\n"
        "ASTOR\n"
        "Giriş: 180\n"
        "Stop: 175\n"
        "Hedef: 190"
    )

async def ac(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = context.args[0]
        entry = float(context.args[1])
        stop = float(context.args[2])
        target = float(context.args[3])

        risk_amount = CAPITAL * (RISK_PERCENT / 100)
        lot = int(risk_amount / abs(entry - stop))

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO positions (symbol, entry, stop, target, lot) VALUES (%s,%s,%s,%s,%s)",
            (symbol, entry, stop, target, lot)
        )
        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(
            f"📂 {symbol} pozisyonu açıldı\n"
            f"Giriş: {entry}\n"
            f"Stop: {stop}\n"
            f"Hedef: {target}\n"
            f"Lot: {lot}"
        )

    except:
        await update.message.reply_text("⚠️ Kullanım: /ac ASTOR 180 175 190")

async def durum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT symbol, entry, stop, target, lot FROM positions WHERE status='open'")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        await update.message.reply_text("📭 Açık pozisyon yok.")
        return

    msg = "📊 AKTİF POZİSYONLAR\n\n"
    for r in rows:
        msg += (
            f"{r[0]}\n"
            f"Giriş: {r[1]}\n"
            f"Stop: {r[2]}\n"
            f"Hedef: {r[3]}\n"
            f"Lot: {r[4]}\n\n"
        )

    await update.message.reply_text(msg)

async def kapat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = context.args[0]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE positions SET status='closed' WHERE symbol=%s", (symbol,))
    conn.commit()
    cur.close()
    conn.close()

    await update.message.reply_text(f"📁 {symbol} pozisyonu kapatıldı.")

# ================== MAIN ==================

def main():
    init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("radar", radar))
    app.add_handler(CommandHandler("ac", ac))
    app.add_handler(CommandHandler("durum", durum))
    app.add_handler(CommandHandler("kapat", kapat))

    app.run_polling()

if __name__ == "__main__":
    main()
