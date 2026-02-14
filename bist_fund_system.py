import os
import requests
import pandas as pd
import yfinance as yf


# ==============================
# TELEGRAM
# ==============================
TELEGRAM_TOKEN = os.getenv("8440357756:AAHjY_XiqJv36QRDZmIk0P3-9I-9A1Qbg68")
TELEGRAM_CHAT_ID = os.getenv("1790584407")


def send_telegram(msg: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram secret yok")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    print("Telegram cevap:", r.text)


# ==============================
# HİSSELER
# ==============================
BIST_LIST = [
    "AKBNK.IS","THYAO.IS","SISE.IS","EREGL.IS","TUPRS.IS",
    "ASELS.IS","BIMAS.IS","KCHOL.IS","GARAN.IS","YKBNK.IS"
]


# ==============================
# SKOR HESABI
# ==============================
def hisse_skoru(ticker: str):
    try:
        df = yf.download(ticker, period="6mo", progress=False)

        if df.empty or len(df) < 30:
            return None

        close = df["Close"]

        momentum = float(close.iloc[-1] / close.iloc[-20] - 1)
        volatility = float(close.pct_change().std())

        if volatility == 0:
            return None

        score = momentum / volatility
        price = float(close.iloc[-1])

        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss
        rsi = float(100 - (100 / (1 + rs.iloc[-1])))

        return {
            "ticker": ticker,
            "score": score,
            "price": price,
            "rsi": rsi
        }

    except Exception as e:
        print("Hata:", ticker, e)
        return None


# ==============================
# PORTFÖY SEÇ
# ==============================
def portfoy_sec():

    sonuc = []

    for h in BIST_LIST:
        s = hisse_skoru(h)
        if s:
            sonuc.append(s)

    if len(sonuc) == 0:
        return pd.DataFrame(), pd.DataFrame()

    df = pd.DataFrame(sonuc).sort_values("score", ascending=False)

    return df.head(3), df


# ==============================
# RAPOR
# ==============================
def rapor_olustur(sec, tum):

    msg = "📊 BIST AI PORTFÖY RAPORU\n\n"

    if sec.empty:
        return msg + "Bugün güçlü sinyal yok."

    msg += "🚀 ÖNERİLEN 3 HİSSE:\n"

    for _, r in sec.iterrows():
        msg += f"{r['ticker']} → {r['price']:.2f} TL | RSI {r['rsi']:.1f}\n"

    msg += "\n📈 TÜM SKORLAR:\n"

    for _, r in tum.iterrows():
        msg += f"{r['ticker']} → Skor {r['score']:.2f}\n"

    return msg


# ==============================
# MAIN
# ==============================
def main():
    print("AI Fon Yöneticisi çalışıyor...")

    sec, tum = portfoy_sec()

    mesaj = rapor_olustur(sec, tum)

    print(mesaj)
    send_telegram(mesaj)


if __name__ == "__main__":
    main()
