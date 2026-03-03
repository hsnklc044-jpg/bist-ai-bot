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

MAX_TOPLAM_RISK = 0.05  # %5 portföy riski

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
            baslangic_risk FLOAT,
            aktif BOOLEAN DEFAULT TRUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS performans (
            id SERIAL PRIMARY KEY,
            sembol TEXT,
            R FLOAT,
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

# ================= RİSK KONTROL =================

def toplam_risk():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT SUM(baslangic_risk) FROM pozisyon WHERE aktif = TRUE")
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row[0] else 0

# ================= KOMUTLAR =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏛 Kurumsal Motor v3 Aktif")

async def pozisyon_ac(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sembol = context.args[0].upper()
        giris = float(context.args[1])
        stop = float(context.args[2])
        hedef = float(context.args[3])

        risk = giris - stop

        if toplam_risk() + risk > MAX_TOPLAM_RISK:
            await update.message.reply_text("⚠️ Toplam portföy risk limiti aşılıyor.")
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO pozisyon (sembol, giris, stop, hedef, baslangic_risk, aktif)
            VALUES (%s, %s, %s, %s, %s, TRUE)
        """, (sembol, giris, stop, hedef, risk))

        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(f"📂 {sembol} pozisyonu açıldı.")

    except:
        await update.message.reply_text("⚠️ Kullanım: /ac ASTOR 180 175 190")

async def performans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), SUM(R) FROM performans")
    count, toplam_R = cur.fetchone()
    cur.close()
    conn.close()

    await update.message.reply_text(
        f"""📊 Performans

Toplam İşlem: {count}
Toplam R: {round(toplam_R if toplam_R else 0,2)}"""
    )

# ================= OTOMATİK MOTOR =================

async def otomatik_kontrol(context: ContextTypes.DEFAULT_TYPE):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, sembol, giris, stop, hedef, baslangic_risk FROM pozisyon WHERE aktif = TRUE")
    rows = cur.fetchall()

    for row in rows:
        poz_id, sembol, giris, stop, hedef, risk = row
        fiyat = fiyat_getir(sembol)

        if fiyat is None:
            continue

        R = (fiyat - giris) / risk

        if fiyat <= stop or fiyat >= hedef:

            cur.execute("UPDATE pozisyon SET aktif = FALSE WHERE id = %s", (poz_id,))
            cur.execute("INSERT INTO performans (sembol, R) VALUES (%s, %s)", (sembol, R))
            conn.commit()

            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=f"🔔 {sembol} kapandı\nR: {round(R,2)}"
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

    print("🏛 Kurumsal Motor v3 Başladı")
    app.run_polling()

if __name__ == "__main__":
    main()
