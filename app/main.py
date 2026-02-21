import os
import time
import requests
import yfinance as yf
import pandas as pd
from fastapi import FastAPI, Request
from datetime import datetime

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AUTHORIZED_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

# CACHE
last_scan_time = 0
cached_result = None

BIST30 = [
    "AKBNK.IS","ALARK.IS","ASELS.IS","BIMAS.IS","EKGYO.IS",
    "ENKAI.IS","EREGL.IS","FROTO.IS","GARAN.IS","HEKTS.IS",
    "ISCTR.IS","KCHOL.IS","KRDMD.IS","ODAS.IS","PETKM.IS",
    "PGSUS.IS","SAHOL.IS","SISE.IS","TAVHL.IS","TCELL.IS",
    "THYAO.IS","TOASO.IS","TUPRS.IS","YKBNK.IS","ZOREN.IS",
    "GUBRF.IS","HALKB.IS","KOZAA.IS","KOZAL.IS","SASA.IS"
]

# RSI
def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# Telegram Send
def send_telegram(text, chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, data=payload)

# ROOT
@app.get("/")
def root():
    return {"status": "BIST AI PRO LOCKED"}

# SCAN ENGINE (Cache'li)
def scan_market():

    global last_scan_time, cached_result

    now = time.time()

    # 60 saniye cache
    if cached_result and now - last_scan_time < 60:
        return cached_result

    breakout, trend, dip = [], [], []

    for symbol in BIST30:
        try:
            df = yf.Ticker(symbol).history(period="6mo")
            if df.empty:
                continue

            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()
            df["RSI"] = calculate_rsi(df["Close"])

            latest = df.iloc[-1]

            close = float(latest["Close"])
            rsi = float(latest["RSI"])
            ma20 = float(latest["MA20"])
            ma50 = float(latest["MA50"])

            score = 0
            if close > ma20: score += 2
            if ma20 > ma50: score += 2
            if rsi > 55: score += 2
            if rsi > 60: score += 1

            data = {
                "symbol": symbol.replace(".IS",""),
                "close": round(close,2),
                "rsi": round(rsi,2),
                "score": score
            }

            if close > ma20 and ma20 > ma50 and rsi > 60:
                breakout.append(data)
            elif close > ma20 and rsi > 48:
                trend.append(data)
            elif 40 < rsi < 48:
                dip.append(data)

            time.sleep(0.4)

        except:
            continue

    pge = round(
        ((len(breakout)*3)+(len(trend)*2)+(len(dip)*1))
        /(len(BIST30)*3)*100,2
    )

    result = (pge, breakout, trend, dip)

    cached_result = result
    last_scan_time = now

    return result

# TELEGRAM WEBHOOK
@app.post("/telegram")
async def telegram_webhook(request: Request):

    data = await request.json()

    if "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text","")

    # 🔒 KİLİT
    if chat_id != AUTHORIZED_CHAT_ID:
        return {"ok": True}

    if text == "/start":
        menu = """
📊 BIST AI PRO PANEL

/scan → Anlık Tarama
/breakout → Breakout
/top3 → En Güçlü 3
/yorum → Piyasa Yorumu
"""
        send_telegram(menu, chat_id)

    elif text == "/scan":
        pge, _, _, _ = scan_market()
        send_telegram(f"📊 PGE: %{pge}", chat_id)

    elif text == "/breakout":
        _, breakout, _, _ = scan_market()
        if not breakout:
            send_telegram("Breakout yok.", chat_id)
        else:
            msg = "🚀 BREAKOUT\n"
            for h in breakout:
                msg += f"{h['symbol']} RSI:{h['rsi']} Skor:{h['score']}\n"
            send_telegram(msg, chat_id)

    elif text == "/top3":
        _, breakout, trend, dip = scan_market()
        all_stocks = breakout + trend + dip
        top3 = sorted(all_stocks, key=lambda x: x["score"], reverse=True)[:3]

        msg = "🏆 TOP 3\n"
        for h in top3:
            msg += f"{h['symbol']} RSI:{h['rsi']} Skor:{h['score']}\n"
        send_telegram(msg, chat_id)

    elif text == "/yorum":
        pge, _, _, _ = scan_market()
        if pge < 30:
            yorum = "⚠️ Zayıf"
        elif pge < 50:
            yorum = "⏳ Nötr"
        elif pge < 70:
            yorum = "💪 Güçlü"
        else:
            yorum = "🚀 Çok Güçlü"

        send_telegram(f"🧠 {yorum} (%{pge})", chat_id)

    return {"ok": True}
