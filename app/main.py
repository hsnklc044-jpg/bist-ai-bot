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

@app.get("/")
def root():
    return {"status": "BIST AI BOT ÇALIŞIYOR"}

@app.get("/test")
def test():
    ticker = yf.Ticker("ASELS.IS")
    df = ticker.history(period="1mo", interval="1d")
    return {
        "veri_satiri": len(df),
        "bos_mu": df.empty
    }

@app.get("/scan")
def scan():

    breakout_list = []
    trend_list = []
    dip_list = []

    total_score_sum = 0
    valid_symbol_count = 0

    for symbol in BIST30:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo", interval="1d")

            # 🔥 ÖNEMLİ DÜZELTME
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

            if pd.isna(latest["RSI"]) or pd.isna(latest["MA20"]):
                continue

            score, signal = calculate_score(latest)

            total_score_sum += score
            valid_symbol_count += 1

            # 🔴 BREAKOUT
            if (
                latest["Close"] >= latest["HH20"]
                and latest["Volume"] > latest["VOL_AVG20"] * 1.3
                and latest["RSI"] > 60
            ):
                breakout_list.append({
                    "symbol": symbol.replace(".IS",""),
                    "close": round(float(latest["Close"]),2),
                    "rsi": round(float(latest["RSI"]),2),
                    "score": score,
                    "signal": "BREAKOUT"
                })

            # 🟡 TREND
            elif (
                latest["Close"] > latest["MA20"]
                and latest["MA20"] > latest["MA50"]
                and latest["RSI"] > 50
            ):
                trend_list.append({
                    "symbol": symbol.replace(".IS",""),
                    "close": round(float(latest["Close"]),2),
                    "rsi": round(float(latest["RSI"]),2),
                    "score": score,
                    "signal": "TREND"
                })

            # 🔵 DİP
            elif (
                latest["RSI"] > 40
                and latest["RSI"] < 48
                and df["RSI"].iloc[-1] > df["RSI"].iloc[-2]
            ):
                dip_list.append({
                    "symbol": symbol.replace(".IS",""),
                    "close": round(float(latest["Close"]),2),
                    "rsi": round(float(latest["RSI"]),2),
                    "score": score,
                    "signal": "DIP TOPARLANMA"
                })

        except:
            continue

    # 🎯 PİYASA GÜÇ ENDEKSİ
    if valid_symbol_count > 0:
        pge = round((total_score_sum / (valid_symbol_count * 10)) * 100, 2)
    else:
        pge = 0

    if pge > 70:
        durum = "GÜÇLÜ"
    elif pge > 50:
        durum = "NÖTR"
    else:
        durum = "ZAYIF"

    return {
        "piyasa_guc_endeksi": pge,
        "durum": durum,
        "veri_alinan_hisse": valid_symbol_count,
        "breakout_sayisi": len(breakout_list),
        "trend_sayisi": len(trend_list),
        "dip_sayisi": len(dip_list),
        "breakout": sorted(breakout_list, key=lambda x: x["score"], reverse=True),
        "trend": sorted(trend_list, key=lambda x: x["score"], reverse=True),
        "dip": sorted(dip_list, key=lambda x: x["score"], reverse=True)
    }
