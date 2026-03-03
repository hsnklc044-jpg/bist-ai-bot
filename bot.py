import os
import logging
import psycopg2
import numpy as np
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import matplotlib.pyplot as plt
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# ================= DB ================= #

def get_connection():
    url = urlparse(DATABASE_URL)
    return psycopg2.connect(
        host=url.hostname,
        port=url.port,
        user=url.username,
        password=url.password,
        dbname=url.path[1:]
    )

def ensure_user(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM settings WHERE user_id=%s;", (user_id,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(
            "INSERT INTO settings (user_id, capital, risk_percent) VALUES (%s,0,1);",
            (user_id,)
        )

    conn.commit()
    cur.close()
    conn.close()

def get_settings(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT capital, risk_percent FROM settings WHERE user_id=%s;",
        (user_id,)
    )
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data

def update_setting(user_id, field, value):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        f"UPDATE settings SET {field}=%s WHERE user_id=%s;",
        (value, user_id)
    )
    conn.commit()
    cur.close()
    conn.close()

# ================= COMMANDS ================= #

async def setcapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    try:
        capital = float(context.args[0])
        update_setting(user_id, "capital", capital)
        await update.message.reply_text(f"💰 Sermaye: {capital}")
    except:
        await update.message.reply_text("❌ /setcapital 100000")

async def setrisk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    try:
        risk = float(context.args[0])
        update_setting(user_id, "risk_percent", risk)
        await update.message.reply_text(f"🎯 Risk %: %{risk}")
    except:
        await update.message.reply_text("❌ /setrisk 1")

# ================= OPEN ================= #

async def open_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    try:
        capital, risk_percent = get_settings(user_id)

        if capital == 0:
            await update.message.reply_text("Önce /setcapital gir.")
            return

        parts = update.message.text.split()
        if len(parts) != 5:
            await update.message.reply_text("❌ /open EREGL long 50 48")
            return

        _, symbol, side, entry, stop = parts
        entry = float(entry)
        stop = float(stop)

        stop_distance = abs(entry - stop)
        risk_amount = capital * (risk_percent / 100)
        lot = risk_amount / stop_distance

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT SUM(ABS(entry - stop) * lot)
        FROM trades
        WHERE user_id=%s AND status='open';
        """, (user_id,))

        current_risk = cur.fetchone()[0] or 0

        if current_risk + risk_amount > capital * 0.05:
            await update.message.reply_text("🚫 %5 açık risk limiti.")
            return

        cur.execute("""
        INSERT INTO trades (user_id, symbol, side, entry, stop, lot, status)
        VALUES (%s,%s,%s,%s,%s,%s,'open')
        """, (user_id, symbol.upper(), side.lower(), entry, stop, lot))

        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(
            f"📥 {symbol} {side}\nLot:{round(lot,2)}"
        )

    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Sistem hatası.")

# ================= CLOSE ================= #

async def close_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    try:
        exit_price = float(context.args[0])

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT id, symbol, side, entry, lot
        FROM trades
        WHERE user_id=%s AND status='open'
        ORDER BY id DESC LIMIT 1;
        """, (user_id,))

        trade = cur.fetchone()

        if not trade:
            await update.message.reply_text("Açık pozisyon yok.")
            return

        trade_id, symbol, side, entry, lot = trade

        pnl = (exit_price - entry) * lot if side=="long" else (entry - exit_price) * lot

        cur.execute("""
        UPDATE trades
        SET exit=%s, pnl=%s, status='closed'
        WHERE id=%s;
        """, (exit_price, pnl, trade_id))

        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(
            f"📤 {symbol} kapandı\nPnL: {round(pnl,2)}"
        )

    except:
        await update.message.reply_text("❌ /close 45")

# ================= EQUITY ================= #

async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT pnl FROM trades
    WHERE user_id=%s AND status='closed'
    ORDER BY id;
    """, (user_id,))

    rows = cur.fetchall()

    if not rows:
        await update.message.reply_text("Kapanmış trade yok.")
        return

    pnls = np.array([r[0] for r in rows])
    cumulative = np.cumsum(pnls)
    peak = np.maximum.accumulate(cumulative)
    max_dd = np.max(peak - cumulative)

    plt.figure()
    plt.plot(cumulative)
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    await update.message.reply_text(
        f"📊 Net: {round(np.sum(pnls),2)}\nMaxDD: {round(max_dd,2)}"
    )
    await update.message.reply_photo(photo=buffer)

    cur.close()
    conn.close()

# ================= MAIN ================= #

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("setcapital", setcapital))
    app.add_handler(CommandHandler("setrisk", setrisk))
    app.add_handler(CommandHandler("open", open_trade))
    app.add_handler(CommandHandler("close", close_trade))
    app.add_handler(CommandHandler("equity", equity))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
