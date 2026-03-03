import os
import logging
import psycopg2
import random
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

# ================= DATABASE ================= #

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
        stop FLOAT,
        exit FLOAT,
        lot FLOAT DEFAULT 0,
        pnl FLOAT DEFAULT 0,
        status TEXT DEFAULT 'open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id SERIAL PRIMARY KEY,
        capital FLOAT DEFAULT 0,
        risk_percent FLOAT DEFAULT 1
    );
    """)

    cur.execute("""
    INSERT INTO settings (capital, risk_percent)
    SELECT 0,1
    WHERE NOT EXISTS (SELECT 1 FROM settings);
    """)

    conn.commit()
    cur.close()
    conn.close()

# ================= SETTINGS ================= #

def get_settings():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT capital, risk_percent FROM settings LIMIT 1;")
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

async def setcapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        capital = float(context.args[0])
        update_setting("capital", capital)
        await update.message.reply_text(f"💰 Sermaye: {capital}")
    except:
        await update.message.reply_text("❌ /setcapital 100000")

async def setrisk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        risk = float(context.args[0])
        update_setting("risk_percent", risk)
        await update.message.reply_text(f"🎯 Risk %: %{risk}")
    except:
        await update.message.reply_text("❌ /setrisk 1")

# ================= OPEN ================= #

async def open_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        capital, risk_percent = get_settings()

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
        if stop_distance == 0:
            await update.message.reply_text("Stop mesafesi 0 olamaz.")
            return

        risk_amount = capital * (risk_percent / 100)
        lot = risk_amount / stop_distance

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT SUM(ABS(entry - stop) * lot)
        FROM trades WHERE status='open';
        """)
        current_risk = cur.fetchone()[0] or 0

        if current_risk + risk_amount > capital * 0.05:
            await update.message.reply_text("🚫 %5 toplam açık risk limiti.")
            cur.close(); conn.close()
            return

        cur.execute("""
        INSERT INTO trades (symbol, side, entry, stop, lot, status)
        VALUES (%s,%s,%s,%s,%s,'open')
        """, (symbol.upper(), side.lower(), entry, stop, lot))

        conn.commit()
        cur.close(); conn.close()

        await update.message.reply_text(
            f"📥 {symbol} {side}\nEntry:{entry}\nStop:{stop}\nLot:{round(lot,2)}"
        )

    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Sistem hatası.")

# ================= CLOSE ================= #

async def close_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        exit_price = float(context.args[0])

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT id, symbol, side, entry, lot
        FROM trades WHERE status='open'
        ORDER BY id DESC LIMIT 1;
        """)
        trade = cur.fetchone()

        if not trade:
            await update.message.reply_text("Açık pozisyon yok.")
            return

        trade_id, symbol, side, entry, lot = trade

        pnl = (exit_price - entry) * lot if side=="long" else (entry - exit_price) * lot

        cur.execute("""
        UPDATE trades
        SET exit=%s, pnl=%s, status='closed'
        WHERE id=%s
        """, (exit_price, pnl, trade_id))

        conn.commit()
        cur.close(); conn.close()

        await update.message.reply_text(
            f"📤 {symbol} kapandı\nPnL: {round(pnl,2)}"
        )

    except:
        await update.message.reply_text("❌ /close 45")

# ================= EQUITY ================= #

async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT pnl FROM trades WHERE status='closed' ORDER BY id;")
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

    cur.close(); conn.close()

# ================= KELLY ================= #

async def kelly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT pnl FROM trades WHERE status='closed';")
    rows = cur.fetchall()

    if len(rows) < 5:
        await update.message.reply_text("En az 5 trade gerekli.")
        return

    pnls = np.array([r[0] for r in rows])
    wins = pnls[pnls>0]
    losses = pnls[pnls<0]

    win_rate = len(wins)/len(pnls)
    avg_win = np.mean(wins)
    avg_loss = abs(np.mean(losses))

    rr = avg_win/avg_loss if avg_loss!=0 else 0
    kelly_fraction = win_rate - ((1-win_rate)/rr) if rr!=0 else 0

    await update.message.reply_text(
        f"📊 Kelly Optimal: %{round(kelly_fraction*100,2)}"
    )

    cur.close(); conn.close()

# ================= MONTE CARLO ================= #

async def montecarlo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT pnl FROM trades WHERE status='closed';")
    rows = cur.fetchall()

    if len(rows) < 5:
        await update.message.reply_text("En az 5 trade gerekli.")
        return

    pnls = [r[0] for r in rows]
    simulations = 1000
    trade_count = len(pnls)

    results = []

    for _ in range(simulations):
        sample = random.choices(pnls, k=trade_count)
        results.append(sum(sample))

    await update.message.reply_text(
        f"🎲 Ortalama Final: {round(np.mean(results),2)}\nEn Kötü: {round(min(results),2)}"
    )

    cur.close(); conn.close()

# ================= METRICS ================= #

async def metrics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT pnl FROM trades WHERE status='closed';")
    rows = cur.fetchall()

    if len(rows) < 5:
        await update.message.reply_text("En az 5 trade gerekli.")
        return

    pnls = np.array([r[0] for r in rows])

    mean = np.mean(pnls)
    std = np.std(pnls)
    downside = pnls[pnls<0]
    downside_std = np.std(downside) if len(downside)>0 else 0

    sharpe = mean/std if std!=0 else 0
    sortino = mean/downside_std if downside_std!=0 else 0

    await update.message.reply_text(
        f"📊 Sharpe: {round(sharpe,3)}\nSortino: {round(sortino,3)}"
    )

    cur.close(); conn.close()

# ================= MAIN ================= #

def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("setcapital", setcapital))
    app.add_handler(CommandHandler("setrisk", setrisk))
    app.add_handler(CommandHandler("open", open_trade))
    app.add_handler(CommandHandler("close", close_trade))
    app.add_handler(CommandHandler("equity", equity))
    app.add_handler(CommandHandler("kelly", kelly))
    app.add_handler(CommandHandler("montecarlo", montecarlo))
    app.add_handler(CommandHandler("metrics", metrics))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
