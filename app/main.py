from fastapi import FastAPI
import yfinance as yf
import pandas as pd
import os
import requests

app = FastAPI()

BIST30 = [
    "AKBNK.IS","ALARK.IS","ASELS.IS","BIMAS.IS","EKGYO.IS",
    "ENKAI.IS","EREGL.IS","FROTO.IS","GARAN.IS","HEKTS.IS",
    "ISCTR.IS","KCHOL.IS","KOZAA.IS","KOZAL.IS","KRDMD.IS",
    "ODAS.IS","PETKM.IS","PGSUS.IS","SAHOL.IS","SASA.IS",
    "SISE.IS","TAVHL.IS","TCELL.IS","THYAO.IS","TOASO.IS",
    "TUPRS.IS","YKBNK.IS","ZOREN.IS","GUBRF.IS","HALKB.IS"
]

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)


@app.get("/")
def root():
    return {"status": "BIST AI BOT AKTIF"}


@app.get("/scan")
def scan():

    trend = []
    dip = []

    total_score = 0
    count = 0

    for symbol in BIST30:
        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)

            if df.empty or len(df) < 50:
                continue

            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()

            delta = df["Close"].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)

            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()

            rs = avg_gain / avg_loss
            df["RSI"] = 100 - (100 / (1 + rs))

            latest = df.iloc[-1]

            if pd.isna(latest["RSI"]):
                continue

            score = 0
            if latest["Close"] > latest["MA20"]:
                score += 3
            if latest["MA20"] > latest["MA50"]:
                score += 3
            if latest["RSI"] > 50:
                score += 4

            total_score += score
            count += 1

            if latest["Close"] > latest["MA20"] and latest["RSI"] > 50:
                trend.append({
                    "symbol": symbol.replace(".IS",""),
                    "score": score
                })

            if 40 < latest["RSI"] < 48:
                dip.append({
                    "symbol": symbol.replace(".IS",""),
                    "score": score
                })

        except:
            continue

    if count > 0:
        pge = round((total_score / (count * 10)) * 100, 2)
    else:
        pge = 0

    return {
        "piyasa_guc_endeksi": pge,
        "veri_alinan_hisse": count,
        "trend_sayisi": len(trend),
        "dip_sayisi": len(dip),
        "trend": trend,
        "dip": dip
    }


@app.get("/send_report")
def send_report():

    data = scan()

    message = f"""
📊 *BIST AI RAPOR*

PGE: {data['piyasa_guc_endeksi']}

Trend: {data['trend_sayisi']}
Dip: {data['dip_sayisi']}
"""

    send_telegram_message(message)

    return {"status": "Telegram Gönderildi"}
