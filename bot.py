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
            aktif BOOLEAN DEFAULT TRUE
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

# ================= FİYAT ÇEKME =================

def fiyat_getir(sembol):
    try:
        ticker = yf.Ticker(f"{sembol}.IS")
        data = ticker.history(period="1d", interval="1m")
        if not data.empty:
            return round(data["Close"].iloc[-1], 2)
    except:
        return None
    return None

# ================= KOMUTLAR =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 BIST AI PRO Gerçek Piyasa Aktif")

async def pozisyon_ac(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sembol = context.args[0].upper()
        giris = float(context.args[1])
        stop = float(context.args[2])
        hedef = float(context.args[3])

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM pozisyon WHERE aktif = TRUE")

        cur.execute("""
            INSERT INTO pozisyon (sembol, giris, stop, hedef, aktif)
            VALUES (%s, %s, %s, %s, TRUE)
        """, (sembol, giris, stop, hedef))

        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(f"📂 {sembol} pozisyonu açıldı.")

    except:
        await update.message.reply_text("⚠️ Kullanım: /ac ASTOR 180 175 190")

async def pozisyon_kapat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM pozisyon WHERE aktif = TRUE")
    conn.commit()
    cur.close()
    conn.close()
    await update.message.reply_text("📴 Pozisyon kapatıldı.")

async def durum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT sembol, giris, stop, hedef FROM pozisyon WHERE aktif = TRUE")
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        await update.message.reply_text("📭 Aktif pozisyon yok.")
        return

    sembol, giris, stop, hedef = row
    fiyat = fiyat_getir(sembol)

    await update.message.reply_text(
        f"""📊 AKTİF POZİSYON

Sembol: {sembol}
Anlık Fiyat: {fiyat}
Giriş: {giris}
Stop: {stop}
Hedef: {hedef}"""
    )

# ================= OTOMATİK KONTROL =================

async def otomatik_kontrol(context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, sembol, giris, stop, hedef FROM pozisyon WHERE aktif = TRUE")
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        return

    poz_id, sembol, giris, stop, hedef = row
    fiyat = fiyat_getir(sembol)

    if fiyat is None:
        cur.close()
        conn.close()
        return

    if fiyat <= stop:
        cur.execute("DELETE FROM pozisyon WHERE id = %s", (poz_id,))
        conn.commit()

        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=f"🔴 STOP ÇALIŞTI!\n{sembol}\nFiyat: {fiyat}"
        )

    elif fiyat >= hedef:
        cur.execute("DELETE FROM pozisyon WHERE id = %s", (poz_id,))
        conn.commit()

        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=f"🎯 HEDEF GERÇEKLEŞTİ!\n{sembol}\nFiyat: {fiyat}"
        )

    cur.close()
    conn.close()

# ================= MAIN =================

def main():
    tablo_olustur()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ac", pozisyon_ac))
    app.add_handler(CommandHandler("kapat", pozisyon_kapat))
    app.add_handler(CommandHandler("durum", durum))

    app.job_queue.run_repeating(
        otomatik_kontrol,
        interval=60,
        first=10
    )

    print("🚀 Gerçek piyasa sistemi başladı")
    app.run_polling()

if __name__ == "__main__":
    main()
