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

# ---------------- SETTINGS ---------------- #

def get_settings():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT capital, risk_percent, daily_loss_limit FROM settings LIMIT 1;")
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data

# ---------------- OPEN TRADE ---------------- #

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

# ---------------- CLOSE TRADE ---------------- #

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

# ---------------- EQUITY ---------------- #

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
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("open", open_trade))
    app.add_handler(CommandHandler("close", close_trade))
    app.add_handler(CommandHandler("equity", equity))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
