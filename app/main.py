from fastapi import FastAPI
import yfinance as yf
import pandas as pd

from app import scoring_engine

app = FastAPI()


@app.get("/")
def root():
    return {"status": "BIST Institutional Engine aktif"}


@app.get("/analyze/{symbol}")
def analyze_stock(symbol: str):
    try:
        ticker_symbol = symbol.upper() + ".IS"

        df = yf.download(ticker_symbol, period="6mo", interval="1d")

        if df is None or df.empty:
            return {"error": "Veri bulunamadı"}

        # --- Moving Averages ---
        df["MA20"] = df["Close"].rolling(window=20).mean()
        df["MA50"] = df["Close"].rolling(window=50).mean()

        # --- RSI (14) ---
        delta = df["Close"].diff()

        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()

        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # --- Ortalama Hacim ---
        df["VOL_AVG20"] = df["Volume"].rolling(window=20).mean()

        df = df.dropna()

        if df.empty:
            return {"error": "Yetersiz veri"}

        # --- Skor Hesaplama ---
        score, signal = scoring_engine.calculate_score(df)

        latest = df.iloc[-1]

        return {
            "symbol": symbol.upper(),
            "close": float(latest["Close"]),
            "ma20": float(latest["MA20"]),
            "ma50": float(latest["MA50"]),
            "rsi": float(latest["RSI"]),
            "volume": float(latest["Volume"]),
            "volume_avg20": float(latest["VOL_AVG20"]),
            "score": score,
            "signal": signal
        }

    except Exception as e:
        return {"error": str(e)}
