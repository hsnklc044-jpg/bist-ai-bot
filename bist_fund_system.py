import os
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime

# ================= TELEGRAM =================
TELEGRAM_TOKEN = os.getenv("8440357756:AAGYdwV7WGedN6rhiK7yKZyOSwwLqkb0mqQ")
TELEGRAM_CHAT_ID = os.getenv("1790584407")


def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    requests.post(url, json=payload, timeout=10)


# ================= BIST LIST =================
BIST_TICKERS = [
    "AKBNK.IS", "ASELS.IS", "BIMAS.IS", "EREGL.IS", "FROTO.IS",
    "GARAN.IS", "HEKTS.IS", "KCHOL.IS", "KOZAL.IS", "PGSUS.IS",
    "SAHOL.IS", "SISE.IS", "TAVHL.IS", "TCELL.IS", "THYAO.IS",
    "TOASO.IS", "TUPRS.IS", "YKBNK.IS"
]


# ================= INDICATORS =================
def compute_indicators(df: pd.DataFrame):
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df["TR"] = df[["High", "Close"]].max(axis=1) - df[["Low", "Close"]].min(axis=1)
    df["ATR"] = df["TR"].rolling(14).mean()

    return df


# ================= STOCK FILTER =================
def analyze_stock(ticker: str):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)

        if df.empty or len(df) < 60:
            return None

        df = compute_indicators(df)
        last = df.iloc[-1]

        # Trend
        trend_ok = last["Close"] > last["EMA20"] > last["EMA50"]

        # Momentum
        momentum_ok = last["RSI"] > 50

        # Volume
        vol_mean = df["Volume"].rolling(20).mean().iloc[-1]
        volume_ok = last["Volume"] > vol_mean

        # Risk (ATR / price < 5%)
        risk_ok = (last["ATR"] / last["Close"]) < 0.05

        if trend_ok and momentum_ok and volume_ok and risk_ok:
            score = (
                (last["Close"] / last["EMA20"]) * 0.4
                + (last["RSI"] / 100) * 0.3
                + (last["Volume"] / vol_mean) * 0.3
            )

            return {"ticker": ticker, "score": score}

    except Exception as e:
        print(f"Hata {ticker}: {e}")

    return None


# ================= MAIN =================
def main():
    results = []

    for ticker in BIST_TICKERS:
        data = analyze_stock(ticker)
        if data:
            results.append(data)

    if not results:
        send_telegram("⚠️ Bugün filtreye uyan hisse bulunamadı.")
        return

    # En iyi 5 hisse
    top = sorted(results, key=lambda x: x["score"], reverse=True)[:5]

    date_str = datetime.now().strftime("%d.%m.%Y")

    message = f"📊 *BIST AI FON RAPORU*\nTarih: {date_str}\n\n"

    for i, stock in enumerate(top, 1):
        message += f"{i}️⃣ {stock['ticker']} — Güç skoru: {stock['score']:.2f}\n"

    message += "\nPortföy dağılımı: Her biri %20\n"
    message += "⏰ Saat: 18:10"

    send_telegram(message)


if __name__ == "__main__":
    main()
