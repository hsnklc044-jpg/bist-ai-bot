import yfinance as yf

from app.bist30 import BIST30
from engine.ai_scoring_engine import score_stock
from engine.market_regime_engine import get_market_regime

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

        if len(df) < 60:
            return None

        return df

    except Exception as e:

        print("Veri indirilemedi:", symbol, e)
        return None


def run_scanner():

    print("🚀 BIST AI radar çalışıyor...")

    results = []

    # MARKET DURUMU
    try:

        regime = get_market_regime()

        print("📊 Market Regime:", regime)

        if regime == "BEAR":
            print("📉 Piyasa düşüş trendinde ama radar çalışmaya devam ediyor")

    except Exception as e:

        print("Market regime okunamadı:", e)

    # HİSSE TARAMA
    for symbol in BIST30:

        ticker = f"{symbol}.IS"

        print("Hisse taranıyor:", ticker)

        df = download_data(ticker)

        if df is None:
            continue

        try:

            score = score_stock(df)

            if score is None:
                continue

            price = float(df["Close"].iloc[-1])

            # güçlü hisseleri filtrele
            if score >= 60:

                results.append({
                    "symbol": symbol,
                    "score": score,
                    "price": price
                })

        except Exception as e:

            print("❌ Scanner hata verdi:", symbol, e)

    # SKOR SIRALAMA
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    print("✅ Radar tamamlandı")

    if len(results) > 0:

        print("🏆 En güçlü hisseler:")

        for r in results[:5]:

            print(r["symbol"], "Skor:", r["score"])

    else:

        print("⚠️ Güçlü sinyal bulunamadı")

    return results
