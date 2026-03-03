import os
import logging
import psycopg2
import yfinance as yf
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime, time

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
CHAT_ID = os.getenv("CHAT_ID")

CAPITAL = float(os.getenv("CAPITAL", 100000))
RISK_PERCENT = float(os.getenv("RISK_PERCENT", 1.5))
MAX_PORTFOLIO_RISK = 0.05  # %5

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

# ================= PDF =================

def pdf_olustur(islem_sayisi, toplam_R, toplam_kar, ortalama_R):
    dosya_adi = "gunluk_rapor.pdf"
    c = canvas.Canvas(dosya_adi, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica", 14)
    c.drawString(50, height - 50, "KURUMSAL GUNLUK RAPOR")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Tarih: {datetime.now().strftime('%d-%m-%Y')}")
    c.drawString(50, height - 130, f"Toplam Islem: {islem_sayisi}")
    c.drawString(50, height - 160, f"Toplam R: {round(toplam_R,2)}")
    c.drawString(50, height - 190, f"Toplam Kar: {round(toplam_kar,2)} TL")
    c.drawString(50, height - 220, f"Ortalama R: {round(ortalama_R,2)}")

    c.save()
    return dosya_adi

# ================= KOMUTLAR =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏛 Kurumsal Motor v5 Aktif")

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
    cur.execute("SELECT COUNT(*), SUM(R), SUM(kar), AVG(R) FROM performans")
    count, toplam_R, toplam_kar, ortalama_R = cur.fetchone()
    cur.close()
    conn.close()

    await update.message.reply_text(
        f"""📊 Performans

İşlem: {count}
Toplam R: {round(toplam_R if toplam_R else 0,2)}
Toplam Kar: {round(toplam_kar if toplam_kar else 0,2)} TL"""
    )

async def rapor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), SUM(R), SUM(kar), AVG(R) FROM performans")
    count, toplam_R, toplam_kar, ortalama_R = cur.fetchone()
    cur.close()
    conn.close()

    dosya = pdf_olustur(
        count if count else 0,
        toplam_R if toplam_R else 0,
        toplam_kar if toplam_kar else 0,
        ortalama_R if ortalama_R else 0
    )

    await update.message.reply_document(document=open(dosya, "rb"))

# ================= OTOMATİK MOTOR =================

async def otomatik_kontrol(context: ContextTypes.DEFAULT_TYPE):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, sembol, giris, stop, hedef, lot FROM pozisyon WHERE aktif = TRUE")
    rows = cur.fetchall()

    for row in rows:
        poz_id, sembol, giris, stop, hedef, lot = row
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
    app.add_handler(CommandHandler("rapor", rapor))

    app.job_queue.run_repeating(
        otomatik_kontrol,
        interval=60,
        first=10
    )

    # Her gün 18:10 otomatik rapor
    app.job_queue.run_daily(
        lambda ctx: rapor_oto(ctx),
        time=time(hour=18, minute=10)
    )

    print("🏛 Kurumsal Motor v5 Başladı")
    app.run_polling()

async def rapor_oto(context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), SUM(R), SUM(kar), AVG(R) FROM performans")
    count, toplam_R, toplam_kar, ortalama_R = cur.fetchone()
    cur.close()
    conn.close()

    dosya = pdf_olustur(
        count if count else 0,
        toplam_R if toplam_R else 0,
        toplam_kar if toplam_kar else 0,
        ortalama_R if ortalama_R else 0
    )

    await context.bot.send_document(chat_id=CHAT_ID, document=open(dosya, "rb"))

if __name__ == "__main__":
    main()
