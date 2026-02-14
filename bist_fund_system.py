import yfinance as yf
import pandas as pd
import numpy as np
import requests
import schedule
import time
from datetime import datetime

# TELEGRAM
TOKEN = "8440357756:AAGYdwV7WGedN6rhiK7yKZyOSwwLqkb0mqQ"
CHAT_ID = "1790584407"

# BIST ÖRNEK LİSTE (sonra tüm BIST yapacağız)
HISSELER = [
    "AKBNK.IS","GARAN.IS","YKBNK.IS","EREGL.IS","TUPRS.IS",
    "ASELS.IS","BIMAS.IS","SISE.IS","KCHOL.IS","THYAO.IS"
]

TOPLAM_PARA = 100000


def veri_cek(hisse):
    df = yf.download(hisse, period="6mo", progress=False)
    if df.empty:
        return None
    return df


def skor_hesapla(df):
    close = df["Close"]

    ema20 = close.ewm(span=20).mean().iloc[-1]
    rsi = 100 - (100 / (1 + close.pct_change().add(1).rolling(14).mean().iloc[-1]))

    volatilite = close.pct_change().std()
    getiri = (close.iloc[-1] / close.iloc[0]) - 1

    skor = (
        (close.iloc[-1] > ema20) * 2 +
        (40 < rsi < 70) * 2 +
        (getiri * 5) -
        (volatilite * 10)
    )

    return skor, rsi, close.iloc[-1]


def fon_portfoy():
    sonuc = []

    for hisse in HISSELER:
        df = veri_cek(hisse)
        if df is None:
            continue

        skor, rsi, fiyat = skor_hesapla(df)

        if skor > 0:
            sonuc.append({
                "hisse": hisse,
                "skor": skor,
                "rsi": round(rsi,1),
                "fiyat": round(float(fiyat),2)
            })

    if not sonuc:
        return None

    df = pd.DataFrame(sonuc).sort_values("skor", ascending=False).head(5)

    toplam_skor = df["skor"].sum()
    df["agirlik"] = df["skor"] / toplam_skor
    df["tutar"] = df["agirlik"] * TOPLAM_PARA

    return df


def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": mesaj})


def rapor_olustur():
    portfoy = fon_portfoy()

    if portfoy is None:
        telegram_gonder("❌ Bugün uygun hisse bulunamadı.")
        return

    mesaj = "📊 BIST AI FON RAPORU\n\n"
    mesaj += f"Tarih: {datetime.now().strftime('%d.%m.%Y')}\n"
    mesaj += f"Toplam: {TOPLAM_PARA:,} TL\n\n"

    for _, row in portfoy.iterrows():
        mesaj += (
            f"{row['hisse']} → % {row['agirlik']*100:.1f} | "
            f"{row['tutar']:.0f} TL | RSI {row['rsi']}\n"
        )

    telegram_gonder(mesaj)


def job():
    print("Fon analizi çalıştı:", datetime.now())
    rapor_olustur()


schedule.every().day.at("18:10").do(job)

print("Sistem başlatıldı. Her gün 18:10'da çalışacak.")

while True:
    schedule.run_pending()
    time.sleep(60)
