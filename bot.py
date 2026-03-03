import os
import logging
import psycopg2
import yfinance as yf
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
CHAT_ID = os.getenv("CHAT_ID")

CAPITAL = float(os.getenv("CAPITAL", 100000))
RISK_PERCENT = float(os.getenv("RISK_PERCENT", 1.5))
MAX_PORTFOLIO_RISK = 0.05  # %5 toplam risk

# ================= DB =================

def get_connection():
    url = urlparse(DATABASE_URL)
    return psycopg2.connect(
        host=url.hostname,
        port=url.port,
        user=url.username,
        password=url.password,
        dbname=url.path[1:]
    )

def tablo_olustur():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pozisyon (
            id SERIAL PRIMARY KEY,
            sembol TEXT,
            giris FLOAT,
            stop FLOAT,
            hedef FLOAT,
            lot FLOAT,
            risk_tutar FLOAT,
            aktif BOOLEAN DEFAULT TRUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS performans (
            id SERIAL PRIMARY KEY,
            sembol TEXT,
            R FLOAT,
            kar FLOAT,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

# ================= FİYAT =================

def fiyat_getir(sembol):
    try:
        ticker = yf.Ticker(f"{sembol}.IS")
        data = ticker.history(period="1d", interval="1m")
        if not data.empty:
            return round(data["Close"].iloc[-1], 2)
    except:
        pass
    return None

# ================= RİSK =================

def hesapla_lot(giris, stop):
    risk_mesafe = giris - stop
    risk_para = CAPITAL * (RISK_PERCENT / 100)
    lot = risk_para / risk_mesafe
    return round(lot,2), risk_para

def toplam_portfoy_risk():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT SUM(risk_tutar) FROM pozisyon WHERE aktif = TRUE")
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row[0] else 0

# ================= KOMUTLAR =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏛 Kurumsal Motor v4 Aktif")

async def pozisyon_ac(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sembol = context.args[0].upper()
        giris = float(context.args[1])
        stop = float(context.args[2])
        hedef = float(context.args[3])

        lot, risk_para = hesapla_lot(giris, stop)

        if toplam_portfoy_risk() + risk_para > CAPITAL * MAX_PORTFOLIO_RISK:
            await update.message.reply_text("⚠️ Portföy toplam risk limiti aşılıyor.")
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO pozisyon (sembol, giris, stop, hedef, lot, risk_tutar, aktif)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        """, (sembol, giris, stop, hedef, lot, risk_para))

        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(
            f"""📂 {sembol} açıldı

Lot: {lot}
Risk: {risk_para} TL"""
        )

    except:
        await update.message.reply_text("⚠️ Kullanım: /ac ASTOR 180 175 190")

async def performans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), SUM(R), SUM(kar) FROM performans")
    count, toplam_R, toplam_kar = cur.fetchone()
    cur.close()
    conn.close()

    await update.message.reply_text(
        f"""📊 Performans

İşlem: {count}
Toplam R: {round(toplam_R if toplam_R else 0,2)}
Toplam Kar: {round(toplam_kar if toplam_kar else 0,2)} TL"""
    )

# ================= OTOMATİK MOTOR =================

async def otomatik_kontrol(context: ContextTypes.DEFAULT_TYPE):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, sembol, giris, stop, hedef, lot, risk_tutar FROM pozisyon WHERE aktif = TRUE")
    rows = cur.fetchall()

    for row in rows:
        poz_id, sembol, giris, stop, hedef, lot, risk_para = row
        fiyat = fiyat_getir(sembol)

        if fiyat is None:
            continue

        R = (fiyat - giris) / (giris - stop)
        kar = (fiyat - giris) * lot

        if fiyat <= stop or fiyat >= hedef:

            cur.execute("UPDATE pozisyon SET aktif = FALSE WHERE id = %s", (poz_id,))
            cur.execute("INSERT INTO performans (sembol, R, kar) VALUES (%s, %s, %s)",
                        (sembol, R, kar))
            conn.commit()

            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=f"🔔 {sembol} kapandı\nR: {round(R,2)}\nKar: {round(kar,2)} TL"
            )

    cur.close()
    conn.close()

# ================= MAIN =================

def main():
    tablo_olustur()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ac", pozisyon_ac))
    app.add_handler(CommandHandler("performans", performans))

    app.job_queue.run_repeating(
        otomatik_kontrol,
        interval=60,
        first=10
    )

    print("🏛 Kurumsal Motor v4 Başladı")
    app.run_polling()

if __name__ == "__main__":
    main()
