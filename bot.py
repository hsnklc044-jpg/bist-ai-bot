import os
import logging
import psycopg2
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# ---------------- DATABASE ---------------- #

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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id SERIAL PRIMARY KEY,
        capital FLOAT DEFAULT 0,
        risk_percent FLOAT DEFAULT 1,
        daily_loss_limit FLOAT DEFAULT 3
    );
    """)

    cur.execute("""
    INSERT INTO settings (capital, risk_percent, daily_loss_limit)
    SELECT 0,1,3
    WHERE NOT EXISTS (SELECT 1 FROM settings);
    """)

    conn.commit()
    cur.close()
    conn.close()

def get_settings():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT capital, risk_percent, daily_loss_limit FROM settings LIMIT 1;")
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data

def update_setting(field, value):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE settings SET {field}=%s WHERE id=1;", (value,))
    conn.commit()
    cur.close()
    conn.close()

# ---------------- COMMANDS ---------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Professional Trading Engine Aktif")

# -------- SET CAPITAL -------- #

async def setcapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        capital = float(context.args[0])
        update_setting("capital", capital)
        await update.message.reply_text(f"💰 Sermaye kaydedildi: {capital}")
    except:
        await update.message.reply_text("❌ Kullanım: /setcapital 100000")

# -------- SET RISK -------- #

async def setrisk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        risk = float(context.args[0])
        update_setting("risk_percent", risk)
        await update.message.reply_text(f"🎯 Risk % kaydedildi: %{risk}")
    except:
        await update.message.reply_text("❌ Kullanım: /setrisk 1")

# -------- RISK INFO -------- #

async def risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    capital, risk_percent, _ = get_settings()

    if capital == 0:
        await update.message.reply_text("Önce /setcapital gir.")
        return

    risk_amount = capital * (risk_percent / 100)

    msg = f"""
💰 Sermaye: {capital}
🎯 Risk: %{risk_percent}
📉 Maks Risk: {round(risk_amount,2)}
"""
    await update.message.reply_text(msg)

# -------- POSITION SIZE -------- #

async def position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    capital, risk_percent, _ = get_settings()

    if capital == 0:
        await update.message.reply_text("Önce /setcapital gir.")
        return

    try:
        entry = float(context.args[0])
        stop = float(context.args[1])

        stop_distance = abs(entry - stop)
        if stop_distance == 0:
            await update.message.reply_text("Stop mesafesi 0 olamaz.")
            return

        risk_amount = capital * (risk_percent / 100)
        lot = risk_amount / stop_distance

        msg = f"""
📊 POZİSYON HESABI

💰 Sermaye: {capital}
🎯 Risk: %{risk_percent}
📉 Maks Risk: {round(risk_amount,2)}

📍 Entry: {entry}
🛑 Stop: {stop}
📏 Mesafe: {round(stop_distance,2)}

📦 Lot: {round(lot,2)}
"""
        await update.message.reply_text(msg)

    except:
        await update.message.reply_text("❌ Kullanım: /position 50 48")

# -------- ADD TRADE -------- #

async def addtrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    capital, _, daily_limit = get_settings()

    try:
        _, symbol, side, entry, target = update.message.text.split()
        entry = float(entry)
        target = float(target)

        pnl = target - entry if side.lower() == "long" else entry - target

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT SUM(pnl) FROM trades WHERE created_at::date = CURRENT_DATE;")
        today_pnl = cur.fetchone()[0] or 0

        if capital > 0:
            limit_amount = capital * (daily_limit / 100)
            if today_pnl < -limit_amount:
                await update.message.reply_text("🚫 Günlük zarar limiti aşıldı.")
                return

        cur.execute(
            "INSERT INTO trades (symbol, side, entry, target, pnl) VALUES (%s,%s,%s,%s,%s)",
            (symbol.upper(), side.lower(), entry, target, pnl)
        )

        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(f"✅ Trade kaydedildi. PnL: {round(pnl,2)}")

    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Sistem hatası.")

# -------- EQUITY -------- #

async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT pnl FROM trades ORDER BY id;")
    rows = cur.fetchall()

    if not rows:
        await update.message.reply_text("Henüz trade yok.")
        return

    pnls = [r[0] for r in rows]
    total = len(pnls)
    wins = len([p for p in pnls if p > 0])
    losses = len([p for p in pnls if p < 0])
    net = sum(pnls)
    win_rate = round((wins/total)*100,2)

    cumulative = 0
    peak = 0
    max_dd = 0

    for p in pnls:
        cumulative += p
        peak = max(peak, cumulative)
        max_dd = max(max_dd, peak - cumulative)

    msg = f"""
📊 TRADE PERFORMANS

Toplam: {total}
Kazanan: {wins}
Kaybeden: {losses}
Win Rate: %{win_rate}

💰 Net PnL: {round(net,2)}
📉 Max Drawdown: {round(max_dd,2)}
"""
    await update.message.reply_text(msg)

    cur.close()
    conn.close()

# -------- MAIN -------- #

def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setcapital", setcapital))
    app.add_handler(CommandHandler("setrisk", setrisk))
    app.add_handler(CommandHandler("risk", risk))
    app.add_handler(CommandHandler("position", position))
    app.add_handler(CommandHandler("addtrade", addtrade))
    app.add_handler(CommandHandler("equity", equity))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
