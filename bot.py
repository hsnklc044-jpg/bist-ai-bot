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

# ---------------- SETTINGS COMMANDS ---------------- #

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

# ---------------- OPEN TRADE ---------------- #

async def open_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        capital, risk_percent, _ = get_settings()

        if capital == 0:
            await update.message.reply_text("Önce /setcapital gir.")
            return

        parts = update.message.text.split()
        if len(parts) != 5:
            await update.message.reply_text("❌ Kullanım: /open EREGL long 50 48")
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
        FROM trades
        WHERE status='open';
        """)

        current_risk = cur.fetchone()[0] or 0

        if current_risk + risk_amount > capital * 0.05:
            await update.message.reply_text("🚫 Toplam açık risk limiti (%5) aşılırdı.")
            cur.close()
            conn.close()
            return

        cur.execute("""
        INSERT INTO trades (symbol, side, entry, stop, lot, status)
        VALUES (%s,%s,%s,%s,%s,'open')
        """, (symbol.upper(), side.lower(), entry, stop, lot))

        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(
            f"""
📥 POZİSYON AÇILDI

{symbol} {side}
Entry: {entry}
Stop: {stop}
Risk: {round(risk_amount,2)}
Lot: {round(lot,2)}
"""
        )

    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Sistem hatası.")

# ---------------- CLOSE TRADE ---------------- #

async def close_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        exit_price = float(context.args[0])

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT id, symbol, side, entry, lot
        FROM trades
        WHERE status='open'
        ORDER BY id DESC LIMIT 1;
        """)

        trade = cur.fetchone()

        if not trade:
            await update.message.reply_text("Açık pozisyon yok.")
            return

        trade_id, symbol, side, entry, lot = trade

        if side == "long":
            pnl = (exit_price - entry) * lot
        else:
            pnl = (entry - exit_price) * lot

        cur.execute("""
        UPDATE trades
        SET exit=%s, pnl=%s, status='closed'
        WHERE id=%s
        """, (exit_price, pnl, trade_id))

        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(
            f"""
📤 POZİSYON KAPANDI

{symbol} {side}
Exit: {exit_price}
PnL: {round(pnl,2)}
"""
        )

    except:
        await update.message.reply_text("❌ Kullanım: /close 45")

# ---------------- POSITIONS ---------------- #

async def positions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT symbol, side, entry, stop, lot
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
        msg += f"{r[0]} {r[1]} @ {r[2]} Stop:{r[3]} Lot:{round(r[4],2)}\n"

    await update.message.reply_text(msg)

    cur.close()
    conn.close()

# ---------------- FLOATING ---------------- #

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        current_price = float(context.args[0])

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT symbol, side, entry, lot
        FROM trades
        WHERE status='open'
        ORDER BY id DESC LIMIT 1;
        """)

        trade = cur.fetchone()

        if not trade:
            await update.message.reply_text("Açık pozisyon yok.")
            return

        symbol, side, entry, lot = trade

        if side == "long":
            floating = (current_price - entry) * lot
        else:
            floating = (entry - current_price) * lot

        await update.message.reply_text(
            f"""
📡 FLOATING

{symbol} {side}
Entry: {entry}
Current: {current_price}
Lot: {round(lot,2)}

Floating: {round(floating,2)}
"""
        )

        cur.close()
        conn.close()

    except:
        await update.message.reply_text("❌ Kullanım: /price 47")

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

Total: {len(pnls)}
Net PnL: {round(sum(pnls),2)}
Max DD: {round(max_dd,2)}
"""

    await update.message.reply_text(msg)
    await update.message.reply_photo(photo=buffer)

    cur.close()
    conn.close()

# ---------------- KELLY ---------------- #

async def kelly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT pnl FROM trades WHERE status='closed';")
    rows = cur.fetchall()

    if not rows or len(rows) < 5:
        await update.message.reply_text("Kelly için en az 5 kapanmış trade gerekli.")
        return

    pnls = [r[0] for r in rows]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]

    win_rate = len(wins) / len(pnls)
    avg_win = sum(wins)/len(wins)
    avg_loss = abs(sum(losses)/len(losses))

    if avg_loss == 0:
        await update.message.reply_text("Zarar yok. Kelly hesaplanamaz.")
        return

    rr = avg_win / avg_loss
    kelly_fraction = win_rate - ((1 - win_rate) / rr)
    conservative = kelly_fraction * 0.5

    msg = f"""
📊 KELLY ANALİZİ

Win Rate: %{round(win_rate*100,2)}
RR: {round(rr,2)}

Kelly Optimal: %{round(kelly_fraction*100,2)}
Önerilen Risk: %{round(conservative*100,2)}
"""

    await update.message.reply_text(msg)

    cur.close()
    conn.close()

# ---------------- MONTE CARLO ---------------- #

async def montecarlo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT pnl FROM trades WHERE status='closed';")
    rows = cur.fetchall()

    if not rows or len(rows) < 5:
        await update.message.reply_text("Monte Carlo için en az 5 kapanmış trade gerekli.")
        return

    pnls = [r[0] for r in rows]

    simulations = 1000
    trade_count = len(pnls)

    final_results = []
    worst_dd = 0

    for _ in range(simulations):
        shuffled = random.choices(pnls, k=trade_count)

        cumulative = 0
        peak = 0
        max_dd = 0

        for p in shuffled:
            cumulative += p
            peak = max(peak, cumulative)
            max_dd = max(max_dd, peak - cumulative)

        final_results.append(cumulative)
        worst_dd = max(worst_dd, max_dd)

    avg_final = np.mean(final_results)
    worst_case = min(final_results)

    msg = f"""
🎲 MONTE CARLO

Simülasyon: {simulations}
Trade Sayısı: {trade_count}

Ortalama Final: {round(avg_final,2)}
En Kötü Final: {round(worst_case,2)}
En Kötü Drawdown: {round(worst_dd,2)}
"""

    await update.message.reply_text(msg)

    cur.close()
    conn.close()

# ---------------- MAIN ---------------- #

def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("setcapital", setcapital))
    app.add_handler(CommandHandler("setrisk", setrisk))
    app.add_handler(CommandHandler("open", open_trade))
    app.add_handler(CommandHandler("close", close_trade))
    app.add_handler(CommandHandler("positions", positions))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("equity", equity))
    app.add_handler(CommandHandler("kelly", kelly))
    app.add_handler(CommandHandler("montecarlo", montecarlo))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
