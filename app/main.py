import os
import time
import requests
import yfinance as yf
import pandas as pd
from fastapi import FastAPI

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BIST30 = [
    "AKBNK.IS","ALARK.IS","ASELS.IS","BIMAS.IS","EKGYO.IS",
    "ENKAI.IS","EREGL.IS","FROTO.IS","GARAN.IS","HEKTS.IS",
    "ISCTR.IS","KCHOL.IS","KRDMD.IS","ODAS.IS","PETKM.IS",
    "PGSUS.IS","SAHOL.IS","SISE.IS","TAVHL.IS","TCELL.IS",
    "THYAO.IS","TOASO.IS","TUPRS.IS","YKBNK.IS","ZOREN.IS",
    "GUBRF.IS","HALKB.IS","KOZAA.IS","KOZAL.IS","SASA.IS"
]

def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

@app.get("/")
def root():
    return {"status": "BIST AI BOT AKTIF"}

@app.get("/scan")
def scan_market():

    breakout = []
    trend = []
    dip = []
    hata_listesi = []
    veri_alinan = 0

    for symbol in BIST30:

        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo")

            if df.empty:
                continue

            veri_alinan += 1

            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()
            df["RSI"] = calculate_rsi(df["Close"])

            latest = df.iloc[-1]

            close = float(latest["Close"])
            rsi = float(latest["RSI"])
            ma20 = float(latest["MA20"])
            ma50 = float(latest["MA50"])

            score = 0

            if close > ma20:
                score += 2
            if ma20 > ma50:
                score += 2
            if rsi > 55:
                score += 2
            if rsi > 60:
                score += 1

            # BREAKOUT
            if close > ma20 and ma20 > ma50 and rsi > 60:
                breakout.append({
                    "symbol": symbol.replace(".IS",""),
                    "close": round(close,2),
                    "rsi": round(rsi,2),
                    "score": score
                })

            # TREND
            elif close > ma20 and rsi > 48:
                trend.append({
                    "symbol": symbol.replace(".IS",""),
                    "close": round(close,2),
                    "rsi": round(rsi,2),
                    "score": score
                })

            # DİP
            elif 40 < rsi < 48:
                dip.append({
                    "symbol": symbol.replace(".IS",""),
                    "close": round(close,2),
                    "rsi": round(rsi,2),
                    "score": score
                })

            time.sleep(0.7)  # rate limit koruma

        except Exception as e:
            hata_listesi.append({symbol: str(e)})
            continue

    piyasa_guc = round(
        ((len(breakout)*3)+(len(trend)*2)+(len(dip)*1)) 
        / (len(BIST30)*3) * 100, 2
    )

    return {
        "piyasa_guc_endeksi": piyasa_guc,
        "veri_alinan_hisse": veri_alinan,
        "breakout_sayisi": len(breakout),
        "trend_sayisi": len(trend),
        "dip_sayisi": len(dip),
        "breakout": breakout,
        "trend": trend,
        "dip": dip,
        "hata_sayisi": len(hata_listesi)
    }

@app.get("/send_report")
def send_report():

    result = scan_market()

    mesaj = f"""
📊 BIST AI Günlük Rapor

Piyasa Güç Endeksi: %{result['piyasa_guc_endeksi']}
Veri Alınan Hisse: {result['veri_alinan_hisse']}

🚀 Breakout: {result['breakout_sayisi']}
📈 Trend: {result['trend_sayisi']}
🔄 Dip: {result['dip_sayisi']}
"""

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mesaj
    }

    requests.post(url, data=payload)

    return {"status": "Telegram Gönderildi"}
