from fastapi import FastAPI
import yfinance as yf
import pandas as pd

from app import scoring_engine

app = FastAPI()


# -------------------------------------------------
# ROOT
# -------------------------------------------------
@app.get("/")
def root():
    return {"status": "BIST Institutional Engine aktif"}


# -------------------------------------------------
# TEK HİSSE ANALİZ
# -------------------------------------------------
@app.get("/analyze/{symbol}")
def analyze_stock(symbol: str):
    try:
        ticker_symbol = symbol.upper() + ".IS"

        df = yf.download(ticker_symbol, period="6mo", interval="1d")

        if df is None or df.empty:
            return {"error": "Veri bulunamadı"}

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # ---- Göstergeler ----
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        df["VOL_AVG20"] = df["Volume"].rolling(20).mean()
        df["HH20"] = df["Close"].rolling(20).max()

        df = df.dropna().reset_index()

        if len(df) < 60:
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


# -------------------------------------------------
# TOPLU KURUMSAL TARAMA
# -------------------------------------------------
@app.get("/scan")
def scan_market():

    BIST_LIST = [
        "ASELS", "THYAO", "EREGL", "SISE", "KCHOL",
        "AKBNK", "TUPRS", "BIMAS", "SAHOL", "ISCTR"
    ]

    results = []

    for symbol in BIST_LIST:
        try:
            ticker_symbol = symbol + ".IS"
            df = yf.download(ticker_symbol, period="6mo", interval="1d")

            if df is None or df.empty:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()

            delta = df["Close"].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)

            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()

            rs = avg_gain / avg_loss
            df["RSI"] = 100 - (100 / (1 + rs))

            df["VOL_AVG20"] = df["Volume"].rolling(20).mean()
            df["HH20"] = df["Close"].rolling(20).max()

            df = df.dropna().reset_index()

            if len(df) < 60:
                continue

            latest = df.iloc[-1]

            # 🔥 KURUMSAL FİLTRE
            if (
                latest["Close"] > latest["MA20"]
                and latest["Close"] > latest["MA50"]
                and latest["MA20"] > latest["MA50"]
                and latest["RSI"] > 55
                and latest["Volume"] > latest["VOL_AVG20"]
                and latest["Close"] >= latest["HH20"] * 0.97
            ):

                score, signal = scoring_engine.calculate_score(df)

                results.append({
                    "symbol": symbol,
                    "close": float(latest["Close"]),
                    "score": score,
                    "signal": signal
                })

        except:
            continue

    return sorted(results, key=lambda x: x["score"], reverse=True)
