from fastapi import FastAPI
import yfinance as yf
import pandas as pd
from app.scoring_engine import calculate_score

app = FastAPI()

BIST30 = [
    "AKBNK.IS","ALARK.IS","ASELS.IS","BIMAS.IS","EKGYO.IS",
    "ENKAI.IS","EREGL.IS","FROTO.IS","GARAN.IS","GUBRF.IS",
    "HEKTS.IS","ISCTR.IS","KCHOL.IS","KOZAA.IS","KOZAL.IS",
    "KRDMD.IS","ODAS.IS","PETKM.IS","PGSUS.IS","SAHOL.IS",
    "SISE.IS","TAVHL.IS","TCELL.IS","THYAO.IS","TOASO.IS",
    "TUPRS.IS","YKBNK.IS","SASA.IS","ARCLK.IS","DOHOL.IS"
]

def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


@app.get("/scan")
def scan_market():

    breakout_list = []
    trend_list = []
    dip_list = []

    total_weighted_score = 0
    total_weight = 0

    for symbol in BIST30:
        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)

            if df.empty or len(df) < 50:
                continue

            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()
            df["RSI"] = calculate_rsi(df["Close"])
            df["VOL_AVG20"] = df["Volume"].rolling(20).mean()
            df["HH20"] = df["High"].rolling(20).max()

            latest = df.iloc[-1]
            score, signal = calculate_score(df)

            # 🔴 BREAKOUT (adaptif yumuşak)
            if (
                latest["Close"] > latest["MA20"]
                and latest["RSI"] > 58
                and latest["Close"] >= latest["HH20"] * 0.99
            ):
                breakout_list.append({
                    "symbol": symbol.replace(".IS",""),
                    "close": round(float(latest["Close"]),2),
                    "rsi": round(float(latest["RSI"]),2),
                    "score": score
                })
                total_weighted_score += score * 3
                total_weight += 3

            # 🟡 TREND
            elif (
                latest["RSI"] > 48
                and latest["Close"] > latest["MA20"]
            ):
                trend_list.append({
                    "symbol": symbol.replace(".IS",""),
                    "close": round(float(latest["Close"]),2),
                    "rsi": round(float(latest["RSI"]),2),
                    "score": score
                })
                total_weighted_score += score * 2
                total_weight += 2

            # 🔵 DIP
            elif (
                38 < latest["RSI"] < 50
                and df["RSI"].iloc[-1] > df["RSI"].iloc[-2]
            ):
                dip_list.append({
                    "symbol": symbol.replace(".IS",""),
                    "close": round(float(latest["Close"]),2),
                    "rsi": round(float(latest["RSI"]),2),
                    "score": score
                })
                total_weighted_score += score
                total_weight += 1

        except:
            continue

    if total_weight > 0:
        pge = round((total_weighted_score / (total_weight * 10)) * 100, 2)
    else:
        pge = 0

    if pge > 65:
        durum = "GÜÇLÜ"
    elif pge > 45:
        durum = "NÖTR"
    else:
        durum = "ZAYIF"

    return {
        "piyasa_guc_endeksi": pge,
        "durum": durum,
        "breakout_sayisi": len(breakout_list),
        "trend_sayisi": len(trend_list),
        "dip_sayisi": len(dip_list),
        "breakout": sorted(breakout_list, key=lambda x: x["score"], reverse=True),
        "trend": sorted(trend_list, key=lambda x: x["score"], reverse=True),
        "dip": sorted(dip_list, key=lambda x: x["score"], reverse=True)
    }
