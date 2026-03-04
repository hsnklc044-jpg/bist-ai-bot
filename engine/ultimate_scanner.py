import yfinance as yf

from engine.bist_symbols import BIST_SYMBOLS
from engine.ai_scoring_engine import calculate_ai_score


# ---------------------------------------
# FİYAT ÇEK
# ---------------------------------------

def get_price(symbol):

    try:

        ticker = f"{symbol}.IS"

        data = yf.download(ticker, period="5d", interval="1d")

        if data.empty:
            return None

        price = float(data["Close"].iloc[-1])

        return round(price, 2)

    except Exception as e:

        print(symbol, "fiyat hatası:", e)

        return None


# ---------------------------------------
# ULTRA RADAR
# ---------------------------------------

def run_ultimate_scan():

    print("🚀 ULTRA BIST RADAR BAŞLADI")

    results = []

    for symbol in BIST_SYMBOLS:

        try:

            score = calculate_ai_score(symbol)

            if score is None:
                continue

            # düşük skor filtre
            if score < 70:
                continue

            price = get_price(symbol)

            if price is None:
                continue

            signal = {
                "symbol": symbol,
                "price": price,
                "score": score,
                "signal": "AI AL SİNYALİ"
            }

            results.append(signal)

        except Exception as e:

            print(symbol, "scan hatası:", e)

    results.sort(key=lambda x: x["score"], reverse=True)

    print("✅ Radar tamamlandı")

    return results[:5]
