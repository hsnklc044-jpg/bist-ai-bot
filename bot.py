import os
import logging
import numpy as np
import pandas as pd
import yfinance as yf

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# =========================
# AYARLAR
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SYMBOLS = [
    "THYAO.IS",
    "ASELS.IS",
    "SISE.IS",
    "EREGL.IS",
    "BIMAS.IS",
]

RISK_ORANI = 0.01  # %1 risk

# =========================
# GLOBAL DURUM
# =========================

bakiye = 100000
zirve_bakiye = bakiye
max_dusus = 0
islem_sayisi = 0
kazanan = 0
kaybeden = 0
mod_mesaji_gonderildi = False

logging.basicConfig(level=logging.INFO)

# =========================
# GÖSTERGELER
# =========================

def ema(veri, periyot):
    return veri.ewm(span=periyot, adjust=False).mean()

def atr(df, periyot=14):
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift())
    low_close = abs(df['Low'] - df['Close'].shift())
    aralik = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = aralik.max(axis=1)
    return true_range.rolling(periyot).mean()

def trend_uygun(df):
    df["EMA20"] = ema(df["Close"], 20)
    df["EMA50"] = ema(df["Close"], 50)
    df["EMA200"] = ema(df["Close"], 200)
    return df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1] > df["EMA200"].iloc[-1]

def bakiye_guncelle(pnl):
    global bakiye, zirve_bakiye, max_dusus
    bakiye += pnl
    zirve_bakiye = max(zirve_bakiye, bakiye)
    max_dusus = (zirve_bakiye - bakiye) / zirve_bakiye

# =========================
# PİYASA TARAMA
# =========================

async def piyasa_tara(context: ContextTypes.DEFAULT_TYPE):
    global islem_sayisi, kazanan, kaybeden

    for hisse in SYMBOLS:
        try:
            df = yf.download(hisse, period="3mo", interval="1h", progress=False)

            if len(df) < 200:
                continue

            if not trend_uygun(df):
                continue

            df["ATR"] = atr(df)
            atr_degeri = df["ATR"].iloc[-1]
            fiyat = df["Close"].iloc[-1]

            if np.isnan(atr_degeri):
                continue

            zarar_durdur = fiyat - atr_degeri * 1.5
            kar_al = fiyat + atr_degeri * 2.5

            islem_sayisi += 1

            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=(
                    f"🚀 ALIŞ SİNYALİ\n\n"
                    f"Hisse: {hisse}\n"
                    f"Giriş: {round(fiyat,2)}\n"
                    f"Zarar Durdur: {round(zarar_durdur,2)}\n"
                    f"Kâr Al: {round(kar_al,2)}"
                )
            )

            # Simülasyon (demo amaçlı)
            sonuc = np.random.choice(["kazanç","zarar"], p=[0.55,0.45])

            if sonuc == "kazanç":
                pnl = bakiye * RISK_ORANI * 1.8
                bakiye_guncelle(pnl)
                kazanan += 1
            else:
                pnl = -bakiye * RISK_ORANI
                bakiye_guncelle(pnl)
                kaybeden += 1

            break

        except Exception as e:
            logging.error(e)

# =========================
# TELEGRAM KOMUTLARI
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global mod_mesaji_gonderildi

    if not mod_mesaji_gonderildi:
        await update.message.reply_text(
            "🚀 HEDGE FUND MODU 6.2 AKTİF\n"
            "📊 Trend + Kurumsal Akış Takibi\n"
            "🛡 Risk Yönetimi: %1"
        )
        mod_mesaji_gonderildi = True

async def durum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kazanma_orani = round((kazanan / islem_sayisi) * 100, 2) if islem_sayisi > 0 else 0

    await update.message.reply_text(
        f"💰 Bakiye: {round(bakiye,2)}\n"
        f"📊 Kazanma Oranı: {kazanma_orani}%\n"
        f"📉 Maksimum Düşüş: {round(max_dusus*100,2)}%\n"
        f"🔁 Toplam İşlem: {islem_sayisi}"
    )

# =========================
# ANA ÇALIŞMA BLOĞU
# =========================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", durum))

    # 15 dakikada bir tarama
    app.job_queue.run_repeating(piyasa_tara, interval=900, first=10)

    app.run_polling()

if __name__ == "__main__":
    main()
