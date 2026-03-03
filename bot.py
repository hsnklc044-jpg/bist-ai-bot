import os
import logging
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

# ================= RSI =================

def rsi_hesapla(seri, periyot=14):
    delta = seri.diff()
    kazanc = delta.clip(lower=0).rolling(periyot).mean()
    kayip = -delta.clip(upper=0).rolling(periyot).mean()
    rs = kazanc / kayip
    return 100 - (100 / (1 + rs))

# ================= RS TARAMA =================

HISSELER = ["ASTOR.IS","ASELS.IS","EREGL.IS","BRLSM.IS","KRDMD.IS"]

async def bebek(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("🔥 Lider hisseler taranıyor...")

    semboller = HISSELER + ["XU100.IS"]

    veri = yf.download(
        " ".join(semboller),
        period="3mo",
        interval="1d",
        group_by="ticker",
        progress=False
    )

    endeks = veri["XU100.IS"].dropna()
    endeks_getiri = endeks["Close"].pct_change().iloc[-20:].sum()

    adaylar = []

    for sembol in HISSELER:
        df = veri[sembol].dropna()
        if len(df) < 30:
            continue

        df["EMA20"] = df["Close"].ewm(span=20).mean()
        df["RSI"] = rsi_hesapla(df["Close"])

        hisse_getiri = df["Close"].pct_change().iloc[-20:].sum()
        rs_skor = (hisse_getiri - endeks_getiri) * 100

        son = df.iloc[-1]

        if son["Close"] > son["EMA20"] and son["RSI"] > 50 and rs_skor > 0:

            giris = son["Close"]
            stop = df["Low"].rolling(5).min().iloc[-1]
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

    if not adaylar:
        return await update.message.reply_text("❌ Güçlü trend bulunamadı.")

    await update.message.reply_text("🔥 GÜÇLÜ TREND LİDERLERİ\n\n" + "\n".join(adaylar))


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
            "hedef": hedef
        }

        await update.message.reply_text(f"📂 {sembol} pozisyonu açıldı.")

    except:
        await update.message.reply_text("Kullanım: /ac ASTOR 180 176 190")


# ================= POZİSYON DURUM =================

async def durum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global acik_pozisyon

    if not acik_pozisyon:
        return await update.message.reply_text("Açık pozisyon yok.")

    sembol = acik_pozisyon["sembol"] + ".IS"
    veri = yf.download(sembol, period="5d", interval="1d", progress=False)

    guncel = veri["Close"].iloc[-1]
    giris = acik_pozisyon["giris"]
    stop = acik_pozisyon["stop"]
    hedef = acik_pozisyon["hedef"]

    kar_zarar = (guncel - giris) / giris * 100

    durum_mesaj = "🟢 Pozisyon Aktif"

    if guncel <= stop:
        durum_mesaj = "🔴 STOP ÇALIŞTI"
    elif guncel >= hedef:
        durum_mesaj = "🎯 HEDEF ÇALIŞTI"

    mesaj = (
        f"{durum_mesaj}\n\n"
        f"Hisse: {acik_pozisyon['sembol']}\n"
        f"Güncel Fiyat: {round(guncel,2)}\n"
        f"Kâr/Zarar: %{round(kar_zarar,2)}\n"
        f"Stop: {stop}\n"
        f"Hedef: {hedef}"
    )

    await update.message.reply_text(mesaj)


# ================= POZİSYON KAPAT =================

async def pozisyon_kapat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global acik_pozisyon
    acik_pozisyon = {}
    await update.message.reply_text("📴 Pozisyon kapatıldı.")


# ================= MAIN =================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("bebek", bebek))
    app.add_handler(CommandHandler("ac", pozisyon_ac))
    app.add_handler(CommandHandler("durum", durum))
    app.add_handler(CommandHandler("kapat", pozisyon_kapat))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
