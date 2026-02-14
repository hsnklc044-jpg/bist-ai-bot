import os
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime

TOKEN = os.getenv("8440357756:AAGYdwV7WGedN6rhiK7yKZyOSwwLqkb0mqQ")
CHAT_ID = os.getenv("1790584407")


# ================= TELEGRAM =================
def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})


# ================= BIST LİSTE =================
BIST = [
    "AKBNK.IS","ASELS.IS","BIMAS.IS","EREGL.IS","FROTO.IS",
    "GARAN.IS","KCHOL.IS","KOZAL.IS","PGSUS.IS","SAHOL.IS",
    "SISE.IS","TCELL.IS","THYAO.IS","TUPRS.IS","YKBNK.IS"
]


# ================= ENDEKS FİLTRE =================
def market_ok():
    df = yf.download("XU100.IS", period="6mo", progress=False)

    if df.empty:
        return False

    ma50 = df["Close"].rolling(50).mean().iloc[-1]
    price = df["Close"].iloc[-1]

    return price > ma50


# ================= HİSSE ANALİZ =================
def analyze(ticker):
    try:
        df = yf.download(ticker, period="6mo", progress=False)

        if len(df) < 60:
            return None

        close = df["Close"]

        ema20 = close.ewm(span=20).mean().iloc[-1]
        ema50 = close.ewm(span=50).mean().iloc[-1]

        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rsi = 100 - (100 / (1 + gain.iloc[-1] / loss.iloc[-1]))

        vol = df["Volume"].iloc[-1]
        vol_avg = df["Volume"].rolling(20).mean().iloc[-1]

        atr = (df["High"] - df["Low"]).rolling(14).mean().iloc[-1]

        trend = close.iloc[-1] > ema20 > ema50
        momentum = rsi > 50
        volume_ok = vol > vol_avg
        risk_ok = atr / close.iloc[-1] < 0.05

        if trend and momentum and volume_ok and risk_ok:
            score = (
                (close.iloc[-1] / ema20) * 0.4 +
                (rsi / 100) * 0.3 +
                (vol / vol_avg) * 0.3
            )

            stop = close.iloc[-1] - atr * 2
            target = close.iloc[-1] + atr * 3

            return {
                "ticker": ticker.replace(".IS", ""),
                "score": score,
                "price": round(close.iloc[-1], 2),
                "stop": round(stop, 2),
                "target": round(target, 2)
            }

    except:
        return None


# ================= ANA FON =================
def main():

    # --- Piyasa filtresi ---
    if not market_ok():
        send("📉 Piyasa zayıf.\n\nBugün NAKİTTE BEKLE.")
        return

    results = []

    for t in BIST:
        r = analyze(t)
        if r:
            results.append(r)

    if not results:
        send("⚠️ Uygun hisse bulunamadı.\nBugün işlem yok.")
        return

    # --- En iyi 5 ---
    top = sorted(results, key=lambda x: x["score"], reverse=True)[:5]

    # --- Ağırlıklar (dengeli fon) ---
    weights = [25, 22, 20, 18, 15]

    msg = "📊 TAM OTOMATİK DENGELİ FON\n"
    msg += f"Tarih: {datetime.now().strftime('%d.%m.%Y')}\n\n"

    for i, s in enumerate(top):
        msg += (
            f"{i+1}) {s['ticker']}  (%{weights[i]})\n"
            f"Fiyat: {s['price']} | Stop: {s['stop']} | Hedef: {s['target']}\n\n"
        )

    msg += "Risk seviyesi: ORTA\n"
    msg += "Strateji: Dengeli AI Fon"

    send(msg)


if __name__ == "__main__":
    main()
