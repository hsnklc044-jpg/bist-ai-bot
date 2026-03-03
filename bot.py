import os
import logging
import psycopg2
import yfinance as yf
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
from flask import Flask, render_template_string
import threading

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
CHAT_ID = os.getenv("CHAT_ID")

CAPITAL = float(os.getenv("CAPITAL", 100000))
RISK_PERCENT = float(os.getenv("RISK_PERCENT", 1.5))

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

# ================= TELEGRAM =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏛 Kurumsal Sistem + Dashboard Aktif")

# ================= DASHBOARD =================

app_flask = Flask(__name__)

@app_flask.route("/")
def dashboard():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*), SUM(R), SUM(kar) FROM performans")
    count, toplam_R, toplam_kar = cur.fetchone()

    cur.execute("SELECT COUNT(*) FROM pozisyon WHERE aktif = TRUE")
    aktif_poz = cur.fetchone()[0]

    cur.close()
    conn.close()

    html = f"""
    <html>
    <head>
        <title>Kurumsal Dashboard</title>
        <style>
            body {{ font-family: Arial; background:#111; color:#eee; padding:40px; }}
            .card {{ background:#222; padding:20px; margin:20px 0; border-radius:8px; }}
        </style>
    </head>
    <body>
        <h1>🏛 Kurumsal Portföy Paneli</h1>

        <div class="card">
            <h2>Toplam İşlem</h2>
            <p>{count}</p>
        </div>

        <div class="card">
            <h2>Toplam R</h2>
            <p>{round(toplam_R if toplam_R else 0,2)}</p>
        </div>

        <div class="card">
            <h2>Toplam Kar (TL)</h2>
            <p>{round(toplam_kar if toplam_kar else 0,2)}</p>
        </div>

        <div class="card">
            <h2>Aktif Pozisyon</h2>
            <p>{aktif_poz}</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

# ================= MAIN =================

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app_flask.run(host="0.0.0.0", port=port)

def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

def main():
    threading.Thread(target=run_flask).start()
    run_bot()

if __name__ == "__main__":
    main()
