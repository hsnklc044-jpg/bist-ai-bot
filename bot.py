import os
import logging
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SYMBOLS = ["THYAO.IS","ASELS.IS","SISE.IS","EREGL.IS","BIMAS.IS"]

RISK_ORANI = 0.01
GUNLUK_ZARAR_LIMIT = 0.03

bakiye = 100000
gunluk_baslangic = bakiye
zirve = bakiye
max_dd = 0
toplam_islem = 0
kazanan = 0
kaybeden = 0
acik_pozisyonlar = {}

logging.basicConfig(level=logging.INFO)

# =======================
# GÖSTERGELER
# =======================

def ema(data, p):
    return data.ewm(span=p, adjust=False).mean()

def atr(df, p=14):
    hl = df['High'] - df['Low']
    hc = abs(df['High'] - df['Close'].shift())
    lc = abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([hl,hc,lc],axis=1).max(axis=1)
    return tr.rolling(p).mean()

def trend(df):
    df["EMA20"]=ema(df["Close"],20)
    df["EMA50"]=ema(df["Close"],50)
    df["EMA200"]=ema(df["Close"],200)
    return df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1] > df["EMA200"].iloc[-1]

def bakiye_guncelle(pnl):
    global bakiye, zirve, max_dd
    bakiye += pnl
    zirve = max(zirve,bakiye)
    max_dd = (zirve - bakiye)/zirve

# =======================
# POZİSYON TAKİP
# =======================

async def pozisyon_kontrol(context):
    global kazanan, kaybeden, toplam_islem
    silinecekler = []

    for hisse, poz in acik_pozisyonlar.items():
        df = yf.download(hisse, period="1d", interval="5m", progress=False)
        if len(df) == 0:
            continue

        fiyat = df["Close"].iloc[-1]

        if fiyat <= poz["sl"]:
            pnl = -bakiye * RISK_ORANI
            bakiye_guncelle(pnl)
            kaybeden += 1
            toplam_islem += 1

            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=f"❌ STOP ÇALIŞTI\n{hisse}\nZarar: %{RISK_ORANI*100}"
            )
            silinecekler.append(hisse)

        elif fiyat >= poz["tp"]:
            pnl = bakiye * RISK_ORANI * 2
            bakiye_guncelle(pnl)
            kazanan += 1
            toplam_islem += 1

            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=f"✅ HEDEF GERÇEKLEŞTİ\n{hisse}\nKâr: %{RISK_ORANI*200}"
            )
            silinecekler.append(hisse)

    for s in silinecekler:
        del acik_pozisyonlar[s]

# =======================
# PİYASA TARAMA
# =======================

async def tarama(context):
    global gunluk_baslangic

    if (gunluk_baslangic - bakiye)/gunluk_baslangic >= GUNLUK_ZARAR_LIMIT:
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text="🛑 Günlük maksimum zarar limiti aşıldı. Sistem durduruldu."
        )
        return

    for hisse in SYMBOLS:

        if hisse in acik_pozisyonlar:
            continue

        df = yf.download(hisse, period="3mo", interval="1h", progress=False)
        if len(df) < 200:
            continue

        if not trend(df):
            continue

        df["ATR"]=atr(df)
        atr_val = df["ATR"].iloc[-1]
        fiyat = df["Close"].iloc[-1]

        if np.isnan(atr_val):
            continue

        sl = fiyat - atr_val*1.5
        tp = fiyat + atr_val*2.5

        acik_pozisyonlar[hisse] = {
            "entry":fiyat,
            "sl":sl,
            "tp":tp
        }

        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=(
                f"🚀 YENİ ALIŞ SİNYALİ\n\n"
                f"Hisse: {hisse}\n"
                f"Giriş: {round(fiyat,2)}\n"
                f"Zarar Durdur: {round(sl,2)}\n"
                f"Kâr Al: {round(tp,2)}"
            )
        )

        break

# =======================
# RAPOR
# =======================

async def gunluk_rapor(context):
    kazanma_orani = (kazanan/toplam_islem*100) if toplam_islem>0 else 0

    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=(
            f"📊 GÜNLÜK PERFORMANS RAPORU\n\n"
            f"💰 Bakiye: {round(bakiye,2)}\n"
            f"📈 Kazanma Oranı: %{round(kazanma_orani,2)}\n"
            f"📉 Max Drawdown: %{round(max_dd*100,2)}\n"
            f"🔁 Toplam İşlem: {toplam_islem}"
        )
    )

# =======================
# TELEGRAM
# =======================

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 HEDGE FUND MODE 7.0 AKTİF\n"
        "🛡 Gerçek SL/TP Takibi\n"
        "📊 Günlük Risk Limiti %3"
    )

async def status(update:Update,context:ContextTypes.DEFAULT_TYPE):
    kazanma_orani = (kazanan/toplam_islem*100) if toplam_islem>0 else 0
    await update.message.reply_text(
        f"💰 Bakiye: {round(bakiye,2)}\n"
        f"📊 Winrate: %{round(kazanma_orani,2)}\n"
        f"📉 Drawdown: %{round(max_dd*100,2)}\n"
        f"🔁 İşlem: {toplam_islem}"
    )

# =======================
# MAIN
# =======================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("status",status))

    app.job_queue.run_repeating(tarama, interval=900, first=10)
    app.job_queue.run_repeating(pozisyon_kontrol, interval=300, first=20)
    app.job_queue.run_daily(gunluk_rapor, time=datetime.strptime("18:30","%H:%M").time())

    app.run_polling()

if __name__=="__main__":
    main()
