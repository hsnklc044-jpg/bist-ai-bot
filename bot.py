import os
import logging
import psycopg2
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import matplotlib.pyplot as plt
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# ---------------- DATABASE CONNECTION ---------------- #

def get_connection():
    url = urlparse(DATABASE_URL)
    return psycopg2.connect(
        host=url.hostname,
        port=url.port,
        user=url.username,
        password=url.password,
        dbname=url.path[1:]
    )

# ---------------- INIT DATABASE ---------------- #

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id SERIAL PRIMARY KEY,
        symbol TEXT,
        side TEXT,
        entry FLOAT,
        exit FLOAT,
        pnl FLOAT DEFAULT 0,
        status TEXT DEFAULT 'open',
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

# ---------------- SETTINGS ---------------- #

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
    await update.message.reply_text("🚀 Portfolio Engine Aktif")

# -------- SETTINGS COMMANDS -------- #

async def setcapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        capital = float(context.args[0])
        update_setting("capital", capital)
        await update.message.reply_text(f"💰 Sermaye kaydedildi: {capital}")
    except:
        await update.message.reply_text("❌ Kullanım: /setcapital 100000")

async def setrisk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        risk = float(context.args[0])
        update_setting("risk_percent", risk)
        await update.message.reply_text(f"🎯 Risk % kaydedildi: %{risk}")
    except:
        await update.message.reply_text("❌ Kullanım: /setrisk 1")

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

# -------- OPEN TRADE -------- #

async def open_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        _, symbol, side, entry = update.message.text.split()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO trades (symbol, side, entry, status)
        VALUES (%s,%s,%s,'open')
        """, (symbol.upper(), side.lower(), float(entry)))

        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(f"📥 Pozisyon açıldı: {symbol} {side} @ {entry}")

    except:
        await update.message.reply_text("❌ Kullanım: /open EREGL long 42")

# -------- CLOSE TRADE -------- #

async def close_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        exit_price = float(context.args[0])

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT id, symbol, side, entry
        FROM trades
        WHERE status='open'
        ORDER BY id DESC LIMIT 1
        """)

        trade = cur.fetchone()

        if not trade:
            await update.message.reply_text("Açık pozisyon yok.")
            return

        trade_id, symbol, side, entry = trade

        if side == "long":
            pnl = exit_price - entry
        else:
            pnl = entry - exit_price

        cur.execute("""
        UPDATE trades
        SET exit=%s, pnl=%s, status='closed'
        WHERE id=%s
        """, (exit_price, pnl, trade_id))

        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(
            f"📤 Pozisyon kapandı\n{symbol} {side}\nPnL: {round(pnl,2)}"
        )

    except:
        await update.message.reply_text("❌ Kullanım: /close 45")

# -------- OPEN POSITIONS LIST -------- #

async def positions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, symbol, side, entry
    FROM trades
    WHERE status='open'
    ORDER BY id;
    """)

    rows = cur.fetchall()

    if not rows:
        await update.message.reply_text("Açık pozisyon yok.")
        return

    msg = "📂 AÇIK POZİSYONLAR\n\n"

    for r in rows:
        msg += f"ID: {r[0]} | {r[1]} {r[2]} @ {r[3]}\n"

    await update.message.reply_text(msg)

    cur.close()
    conn.close()

# -------- FLOATING PNL -------- #

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        current_price = float(context.args[0])

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT id, symbol, side, entry
        FROM trades
        WHERE status='open'
        ORDER BY id DESC LIMIT 1;
        """)

        trade = cur.fetchone()

        if not trade:
            await update.message.reply_text("Açık pozisyon yok.")
            return

        trade_id, symbol, side, entry = trade

        if side == "long":
            floating = current_price - entry
        else:
            floating = entry - current_price

        await update.message.reply_text(
            f"""
📡 FLOATING PnL

{symbol} {side}
Entry: {entry}
Current: {current_price}

Floating: {round(floating,2)}
"""
        )

        cur.close()
        conn.close()

    except:
        await update.message.reply_text("❌ Kullanım: /price 47")

# -------- EQUITY + GRAPH -------- #

async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT pnl FROM trades WHERE status='closed' ORDER BY id;")
    rows = cur.fetchall()

    if not rows:
        await update.message.reply_text("Henüz kapanmış trade yok.")
        return

    pnls = [r[0] for r in rows]

    cumulative = 0
    peak = 0
    max_dd = 0
    equity_curve = []

    for p in pnls:
        cumulative += p
        equity_curve.append(cumulative)
        peak = max(peak, cumulative)
        max_dd = max(max_dd, peak - cumulative)

    plt.figure()
    plt.plot(equity_curve)
    plt.title("Equity Curve")
    plt.xlabel("Trade")
    plt.ylabel("Cumulative PnL")

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    msg = f"""
📊 PERFORMANS

Toplam Trade: {len(pnls)}
Net PnL: {round(sum(pnls),2)}
Max Drawdown: {round(max_dd,2)}
"""

    await update.message.reply_text(msg)
    await update.message.reply_photo(photo=buffer)

    cur.close()
    conn.close()

# ---------------- MAIN ---------------- #

def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setcapital", setcapital))
    app.add_handler(CommandHandler("setrisk", setrisk))
    app.add_handler(CommandHandler("risk", risk))
    app.add_handler(CommandHandler("open", open_trade))
    app.add_handler(CommandHandler("close", close_trade))
    app.add_handler(CommandHandler("positions", positions))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("equity", equity))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
