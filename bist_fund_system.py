import os
import requests
import pandas as pd
import numpy as np

try:
    import yfinance as yf
except Exception:
    yf = None


# ================= TELEGRAM =================

TELEGRAM_TOKEN = os.getenv("8440357756:AAHjY_XiqJv36QRDZmIk0P3-9I-9A1Qbg68")
TELEGRAM_CHAT_ID = os.getenv("1790584407")


def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik.")
        print(message)
        return

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Telegram hatası:", e)


# ================= HİSSELER =================

BIST_LIST = [
    "AKBNK.IS", "THYAO.IS", "SISE.IS", "EREGL.IS", "TUPRS.IS",
    "ASELS.IS", "BIMAS.IS", "KCHOL.IS", "GARAN.IS", "YKBNK.IS"
]

RISK_FREE = 0.40


# ================= VERİ =================

def veri_cek(symbol: str):
    if yf is None:
        return None

    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)

        if df is None or df.empty:
            return None

        # Multi-index gelirse düzelt
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return df
    except Exception:
        return None


# ================= RSI =================

def rsi(series: pd.Series, period: int = 14):
    delta = series.diff()

    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()

    rs = gain / loss
    return float((100 - (100 / (1 + rs))).iloc[-1])


# ================= SKOR =================

def hisse_skoru(symbol: str):
    df = veri_cek(symbol)

    if df is None or len(df) < 30:
        return None

    close = df["Close"]

    # 🔥 KRİTİK DÜZELTME
    last_price = close.iloc[-1]
    if isinstance(last_price, pd.Series):
        last_price = last_price.values[0]

    price = float(last_price)

    rsi_val = rsi(close)

    mom = float((close.iloc[-1] / close.iloc[-20]) - 1)
    vol = float(close.pct_change().std())

    if vol == 0:
        return None

    score = (mom - RISK_FREE / 252) / vol

    return {
        "symbol": symbol,
        "price": price,
        "rsi": rsi_val,
        "score": float(score)
    }


# ================= PORTFÖY =================

def portfoy_sec():
    data = []

    for h in BIST_LIST:
        s = hisse_skoru(h)
        if s:
            data.append(s)

    if not data:
        return pd.DataFrame(), pd.DataFrame()

    df = pd.DataFrame(data).sort_values("score", ascending=False)

    return df.head(3), df


# ================= RAPOR =================

def rapor(secilenler, tumu):
    if secilenler is None or secilenler.empty:
        return "⚠️ Bugün sinyal yok."

    text = "📊 BIST AI FON RAPORU\n\n"

    text += "🏆 PORTFÖY:\n"
    for _, r in secilenler.iterrows():
        text += f"{r.symbol} | {r.price:.2f} TL | RSI {r.rsi:.1f}\n"

    text += "\n📈 TÜM SKORLAR:\n"
    for _, r in tumu.iterrows():
        text += f"{r.symbol} → {r.score:.2f}\n"

    return text


# ================= MAIN =================

def main():
    print("AI Fon çalışıyor...")

    sec, tum = portfoy_sec()
    mesaj = rapor(sec, tum)

    print(mesaj)
    send_telegram(mesaj)


if __name__ == "__main__":
    main()
