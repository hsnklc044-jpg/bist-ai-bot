import os
import requests
import traceback
import yfinance as yf
import pandas as pd


TELEGRAM_TOKEN = "8440357756:AAGdYajs2PirEhY2O9R8Voe_JmtAQhIHI8I"
TELEGRAM_CHAT_ID = "1790584407"


def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})


BIST = [
    "AKBNK.IS","THYAO.IS","SISE.IS","EREGL.IS","TUPRS.IS",
    "ASELS.IS","BIMAS.IS","KCHOL.IS","GARAN.IS","YKBNK.IS"
]


def rsi(close, p=14):
    d = close.diff()
    up = d.clip(lower=0).rolling(p).mean()
    down = -d.clip(upper=0).rolling(p).mean()
    rs = up / down
    return 100 - 100 / (1 + rs)


def pick():
    rows = []

    for s in BIST:
        df = yf.download(s, period="6mo", progress=False)
        if df.empty:
            continue

        c = df["Close"]

        score = float((c.iloc[-1] / c.iloc[-20] - 1) / c.pct_change().std())
        r = float(rsi(c).iloc[-1])

        if 40 < r < 70:
            rows.append((s, float(c.iloc[-1]), r, score))

    if not rows:
        return "Bugün uygun hisse yok."

    rows.sort(key=lambda x: x[3], reverse=True)
    top = rows[:5]

    msg = "📊 BIST AI PORTFÖY\n\n"
    for s, p, r, sc in top:
        msg += f"{s} | {p:.2f} TL | RSI {r:.1f} | Skor {sc:.2f}\n"

    return msg


def main():
    try:
        send("🚀 AI motoru başladı")
        msg = pick()
        send(msg)
    except Exception:
        send("❌ HATA\n\n" + traceback.format_exc())


if __name__ == "__main__":
    main()
