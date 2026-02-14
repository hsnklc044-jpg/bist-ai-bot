import os
import requests
import yfinance as yf
import pandas as pd

TELEGRAM_TOKEN = os.getenv("8440357756:AAGdYajs2PirEhY2O9R8Voe_JmtAQhIHI8I")
TELEGRAM_CHAT_ID = os.getenv("1790584407")

BIST_LIST = [
    "AKBNK.IS","THYAO.IS","SISE.IS","EREGL.IS","TUPRS.IS",
    "ASELS.IS","BIMAS.IS","KCHOL.IS","GARAN.IS","YKBNK.IS"
]


def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    r = requests.post(url, data=payload)
    print("Telegram cevap:", r.text)


def hisse_sinyal(symbol):
    df = yf.download(symbol, period="3mo", interval="1d", progress=False)

    if df.empty:
        return None

    close = df["Close"]
    rsi = 100 - (100 / (1 + (close.diff().clip(lower=0).rolling(14).mean() /
                            close.diff().clip(upper=0).abs().rolling(14).mean())))

    last_price = float(close.iloc[-1])
    last_rsi = float(rsi.iloc[-1])

    if last_rsi < 40:
        durum = "AL"
    elif last_rsi > 70:
        durum = "SAT"
    else:
        durum = "BEKLE"

    return f"{symbol} → {durum} | {last_price:.2f} TL | RSI {last_rsi:.1f}"


def main():
    print("BIST AI çalışıyor...")

    mesajlar = []

    for h in BIST_LIST:
        try:
            s = hisse_sinyal(h)
            if s:
                mesajlar.append(s)
        except Exception as e:
            print("Hata:", h, e)

    if not mesajlar:
        mesaj = "Bugün sinyal üretilemedi."
    else:
        mesaj = "📊 BIST AI Sinyalleri\n\n" + "\n".join(mesajlar)

    print(mesaj)
    send_telegram(mesaj)


if __name__ == "__main__":
    main()
