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

        # Moving averages hesapla
        df["MA20"] = df["Close"].rolling(window=20).mean()
        df["MA50"] = df["Close"].rolling(window=50).mean()

        # NaN satırları temizle
        df = df.dropna()

        if df.empty:
            return {"error": "Yetersiz veri"}

        score, signal = scoring_engine.calculate_score(df)

        latest = df.iloc[-1]

        return {
            "symbol": symbol.upper(),
            "close": float(latest["Close"]),
            "ma20": float(latest["MA20"]),
            "ma50": float(latest["MA50"]),
            "score": score,
            "signal": signal
        }

    except Exception as e:
        return {"error": str(e)}
