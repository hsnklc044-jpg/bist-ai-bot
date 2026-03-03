import os
import logging
import asyncio
import yfinance as yf
import pandas as pd
import numpy as np
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
SERMAYE = float(os.getenv("CAPITAL", 100000))
RISK_YUZDE = float(os.getenv("RISK_PERCENT", 1))

acik_pozisyon = {}
son_bildirim = None

# ================= RSI =================

def rsi_hesapla(seri, periyot=14):
    delta = seri.diff()
    kazanc = delta.clip(lower=0).rolling(periyot).mean()
    kayip = -delta.clip(upper=0).rolling(periyot).mean()
    rs = kazanc / kayip
    return 100 - (100 / (1 + rs))

# ================= LİDER TARAMA =================

HISSELER = [
    "ASTOR.IS","ASELS.IS","EREGL.IS",
    "BRLSM.IS","KRDMD.IS","GUBRF.IS","GLYHO.IS"
]

async def bebek(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("🔥 Güçlü trend liderleri taranıyor...")

    try:
        semboller = HISSELER + ["XU100.IS"]

        veri = yf.download(
            " ".join(semboller),
            period="3mo",
            interval="1d",
            group_by="ticker",
            progress=False
        )

        if veri is None or veri.empty:
            return await update.message.reply_text("Veri alınamadı.")

        endeks = veri["XU100.IS"].dropna()
        endeks_getiri = endeks["Close"].pct_change().iloc[-20:].sum()

        adaylar = []

        for sembol in HISSELER:
            try:
                df = veri[sembol].dropna()
                if len(df) < 30:
                    continue

                df["EMA20"] = df["Close"].ewm(span=20).mean()
                df["RSI"] = rsi_hesapla(df["Close"])

                hisse_getiri = df["Close"].pct_change().iloc[-20:].sum()
                rs_skor = (hisse_getiri - endeks_getiri) * 100

                son = df.iloc[-1]

                if son["Close"] > son["EMA20"] and son["RSI"] > 50 and rs_skor > 0:

                    giris = float(son["Close"])
                    stop = float(df["Low"].rolling(5).min().iloc[-1])
                    risk = giris - stop

                    if risk <= 0:
                        continue

                    hedef = giris + risk * 2
                    lot = (SERMAYE * (RISK_YUZDE / 100)) / risk

                    mesaj = (
                        f"📈 {sembol.replace('.IS','')}\n"
                        f"Göreceli Güç: %{round(rs_skor,2)}\n"
                        f"Giriş: {round(giris,2)}\n"
                        f"Stop: {round(stop,2)}\n"
                        f"Hedef: {round(hedef,2)}\n"
                        f"Önerilen Lot: {int(lot)}\n"
                    )

                    adaylar.append(mesaj)

            except:
                continue

        if not adaylar:
            return await update.message.reply_text("❌ Güçlü trend bulunamadı.")

        await update.message.reply_text(
            "🔥 GÜÇLÜ TREND LİDERLERİ\n\n" + "\n".join(adaylar)
        )

    except Exception as e:
        logger.error(e)
        await update.message.reply_text("⚠️ Tarama sırasında hata oluştu.")

# ================= POZİSYON AÇ =================

async def pozisyon_ac(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global acik_pozisyon

    try:
        sembol = context.args[0].upper()
        giris = float(context.args[1])
        stop = float(context.args[2])
        hedef = float(context.args[3])

        acik_pozisyon = {
            "sembol": sembol,
            "giris": giris,
            "stop": stop,
            "hedef": hedef,
            "chat_id": update.effective_chat.id
        }

        await update.message.reply_text(f"📂 {sembol} pozisyonu açıldı.")

    except:
        await update.message.reply_text("Kullanım:\n/ac ASTOR 180 176 190")

# ================= OTOMATİK KONTROL =================

async def otomatik_kontrol(app):

    global acik_pozisyon

    while True:

        if acik_pozisyon:

            try:
                sembol = acik_pozisyon["sembol"]
                sembol_yf = sembol + ".IS"

                veri = yf.download(
                    sembol_yf,
                    period="1d",
                    interval="1m",
                    progress=False
                )

                if veri is None or veri.empty:
                    await asyncio.sleep(60)
                    continue

                guncel = float(veri["Close"].dropna().iloc[-1])

                stop = acik_pozisyon["stop"]
                hedef = acik_pozisyon["hedef"]
                chat_id = acik_pozisyon["chat_id"]

                if guncel <= stop:
                    await app.bot.send_message(
                        chat_id=chat_id,
                        text=f"🔴 STOP ÇALIŞTI!\n{sembol}\nFiyat: {round(guncel,2)}"
                    )
                    acik_pozisyon = {}

                elif guncel >= hedef:
                    await app.bot.send_message(
                        chat_id=chat_id,
                        text=f"🎯 HEDEF GERÇEKLEŞTİ!\n{sembol}\nFiyat: {round(guncel,2)}"
                    )
                    acik_pozisyon = {}

            except Exception as e:
                logger.error(f"Otomatik kontrol hatası: {e}")

        await asyncio.sleep(60)

# ================= MAIN =================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("bebek", bebek))
    app.add_handler(CommandHandler("ac", pozisyon_ac))

    app.create_task(otomatik_kontrol(app))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
