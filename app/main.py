from fastapi import FastAPI
import yfinance as yf
import pandas as pd
from app.scoring_engine import calculate_score

app = FastAPI()

BIST30 = [
    "AKBNK.IS","ALARK.IS","ASELS.IS","BIMAS.IS","EKGYO.IS",
    "ENKAI.IS","EREGL.IS","FROTO.IS","GARAN.IS","HEKTS.IS",
    "ISCTR.IS","KCHOL.IS","KOZAA.IS","KOZAL.IS","KRDMD.IS",
    "ODAS.IS","PETKM.IS","PGSUS.IS","SAHOL.IS","SASA.IS",
    "SISE.IS","TAVHL.IS","TCELL.IS","THYAO.IS","TOASO.IS",
    "TUPRS.IS","YKBNK.IS","ZOREN.IS","GUBRF.IS","HALKB.IS"
]

@app.get("/scan")
def scan():

    breakout_list = []
    trend_list = []
    dip_list = []

    total_score_sum = 0
    valid_symbol_count = 0
    errors = []

    for symbol in BIST30:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo", interval="1d")

            if df is None or df.empty or len(df) < 20:
                continue

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
            df["HH20"] = df["High"].rolling(20).max()

            latest = df.iloc[-1]

            score, signal = calculate_score(latest)

            total_score_sum += score
            valid_symbol_count += 1

        except Exception as e:
            errors.append({symbol: str(e)})
            continue

    if valid_symbol_count > 0:
        pge = round((total_score_sum / (valid_symbol_count * 10)) * 100, 2)
    else:
        pge = 0

    return {
        "piyasa_guc_endeksi": pge,
        "veri_alinan_hisse": valid_symbol_count,
        "hata_sayisi": len(errors),
        "hatalar": errors
    }
