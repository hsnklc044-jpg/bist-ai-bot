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

        # MultiIndex düzelt
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # --- Moving Averages ---
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        # --- RSI (14) ---
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # --- Ortalama Hacim ---
        df["VOL_AVG20"] = df["Volume"].rolling(20).mean()

        # --- 20 Günlük En Yüksek ---
        df["HH20"] = df["Close"].rolling(20).max()

        df = df.dropna().reset_index()

        if df.empty:
            return {"error": "Yetersiz veri"}

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
            "hh20": float(latest["HH20"]),
            "score": score,
            "signal": signal
        }

    except Exception as e:
        return {"error": str(e)}
