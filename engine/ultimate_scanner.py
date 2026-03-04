import yfinance as yf
import pandas as pd

from engine.ai_scoring_engine import score_stock
from engine.market_regime_engine import get_market_regime
from app.bist100 import BIST100


LOOKBACK_PERIOD = "3mo"


def download_data(symbol):

    try:

        df = yf.download(
            symbol,
            period=LOOKBACK_PERIOD,
            interval="1d",
            progress=False
        )

        if df is None or df.empty:
            return None

        df.dropna(inplace=True)

        return df

    except Exception as e:

        print("Veri indirilemedi:", symbol, e)
        return None


def volume_spike(df):

    avg_volume = df["Volume"].rolling(20).mean()

    if df["Volume"].iloc[-1] > avg_volume.iloc[-1] * 1.7:
        return True

    return False


def volatility_squeeze(df):

    rolling_std = df["Close"].rolling(20).std()

    current_vol = rolling_std.iloc[-1]
    avg_vol = rolling_std.mean()

    if current_vol < avg_vol * 0.8:
        return True

    return False


def run_ultimate_scan():

    print("🚀 ULTIMATE BIST AI RADAR BAŞLADI")

    results = []

    # MARKET REGIME
    try:

        regime = get_market_regime()

        print("📊 Market Regime:", regime)

    except Exception as e:

        print("Market regime okunamadı:", e)

    # HİSSE TARAMA
    for symbol in BIST100:

        ticker = f"{symbol}.IS"

        df = download_data(ticker)

        if df is None:
            continue

        if len(df) < 80:
            continue

        try:

            score = score_stock(df)

            vol_spike = volume_spike(df)

            squeeze = volatility_squeeze(df)

            if score >= 60 or (vol_spike and squeeze):

                results.append({
                    "symbol": symbol,
                    "score": score,
                    "volume_spike": vol_spike,
                    "squeeze": squeeze,
                    "price": float(df["Close"].iloc[-1])
                })

        except Exception as e:

            print("Hata:", symbol, e)

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    print("✅ Ultimate Radar tamamlandı")

    if len(results) > 0:

        print("🏆 En güçlü hisseler:")

        for r in results[:10]:

            print(
                r["symbol"],
                "Score:", r["score"],
                "Volume:", r["volume_spike"],
                "Squeeze:", r["squeeze"]
            )

    else:

        print("⚠️ Sinyal bulunamadı")

    return results
