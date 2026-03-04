import yfinance as yf
import pandas as pd

from app.bist30 import BIST30
from app.scoring_engine import score_stock

from engine.market_regime_engine import get_market_regime


LOOKBACK_PERIOD = "6mo"


def download_data(symbol):

    try:

        df = yf.download(symbol, period=LOOKBACK_PERIOD, interval="1d")

        if df.empty:
            return None

        return df

    except Exception as e:

        print(f"Veri indirilemedi: {symbol}", e)

        return None


def run_scanner():

    print("📡 BIST Radar başlıyor...")

    # MARKET REGIME KONTROLÜ
    regime = get_market_regime()

    if regime == "BEAR":

        print("📉 Piyasa düşüş trendinde. Radar durduruldu.")

        return []

    results = []

    for symbol in BIST30:

        ticker = f"{symbol}.IS"

        df = download_data(ticker)

        if df is None:
            continue

        if len(df) < 100:
            continue

        try:

            score = score_stock(df)

            results.append({
                "symbol": symbol,
                "score": score
            })

        except Exception as e:

            print("Skor hesaplanamadı:", symbol, e)

    # SKOR SIRALAMA
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    print("Radar tamamlandı")

    return results
