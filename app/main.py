from fastapi import FastAPI
import yfinance as yf
from app.scoring_engine import calculate_score

app = FastAPI()

BIST30 = [
    "AKBNK.IS","ALARK.IS","ASELS.IS","ASTOR.IS","BIMAS.IS",
    "EKGYO.IS","ENKAI.IS","EREGL.IS","FROTO.IS","GARAN.IS",
    "GUBRF.IS","HEKTS.IS","ISCTR.IS","KCHOL.IS","KOZAL.IS",
    "KOZAA.IS","PETKM.IS","PGSUS.IS","SAHOL.IS","SASA.IS",
    "SISE.IS","TCELL.IS","THYAO.IS","TOASO.IS","TTKOM.IS",
    "TUPRS.IS","YKBNK.IS","ARCLK.IS","ODAS.IS","HALKB.IS"
]

@app.get("/")
def home():
    return {"status": "BIST AI BOT AKTİF"}

@app.get("/scan")
def scan_market():

    breakout_list = []
    preparing_list = []

    for symbol in BIST30:

        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)

            if df.empty or len(df) < 50:
                continue

            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()

            # RSI
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

            # NaN kontrolü
            if latest[["MA20","MA50","RSI","VOL_AVG20","HH20"]].isna().any():
                continue

            score, signal = calculate_score(df)

            # 🔥 BREAKOUT (Trend teyitli - sert filtre)
            if (
                latest["Close"] > latest["MA20"]
                and latest["MA20"] > latest["MA50"]
                and latest["RSI"] > 60
                and latest["Volume"] > latest["VOL_AVG20"] * 1.3
                and latest["Close"] >= latest["HH20"]
            ):
                breakout_list.append({
                    "symbol": symbol.replace(".IS",""),
                    "close": round(float(latest["Close"]),2),
                    "rsi": round(float(latest["RSI"]),2),
                    "score": score,
                    "signal": signal
                })

            # 🟡 HAZIRLANAN (profesyonel erken dönüş)
            elif (
                latest["Close"] > latest["MA20"]
                and latest["RSI"] > 48
                and latest["Close"] >= latest["HH20"] * 0.94
            ):
                preparing_list.append({
                    "symbol": symbol.replace(".IS",""),
                    "close": round(float(latest["Close"]),2),
                    "rsi": round(float(latest["RSI"]),2),
                    "score": score,
                    "signal": signal
                })

        except:
            continue

    breakout_sorted = sorted(breakout_list, key=lambda x: x["score"], reverse=True)
    hazirlanan_sorted = sorted(preparing_list, key=lambda x: x["score"], reverse=True)

    breakout_count = len(breakout_sorted)
    hazirlanan_count = len(hazirlanan_sorted)

    # 📊 Piyasa Güç Endeksi
    pge_raw = (breakout_count * 3) + (hazirlanan_count * 1.5)
    pge = min(round(pge_raw * 2), 100)

    if pge < 10:
        market_state = "ZAYIF"
    elif pge < 25:
        market_state = "TOPLANIYOR"
    elif pge < 40:
        market_state = "GÜÇLENİYOR"
    else:
        market_state = "ÇOK GÜÇLÜ"

    return {
        "piyasa_guc_endeksi": pge,
        "durum": market_state,
        "breakout_sayisi": breakout_count,
        "hazirlanan_sayisi": hazirlanan_count,
        "breakout": breakout_sorted,
        "hazirlanan": hazirlanan_sorted
    }
