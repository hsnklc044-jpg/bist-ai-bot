import yfinance as yf
import pandas as pd

from engine.market_regime_engine import market_regime
from engine.ai_scoring_engine import score_stock
from engine.telegram_engine import send_telegram_message


def run_ultimate_scanner():

    print("🚀 BIST AI radar çalışıyor...")

    # Market regime
    try:
        regime = market_regime()
    except Exception as e:
        print("Market regime error:", e)
        regime = "UNKNOWN"

    print("Market rejimi:", regime)

    # BIST hisseleri (istediğin gibi artırabilirsin)
    bist_stocks = [
        "AEFES.IS","ASELS.IS","BIMAS.IS","EREGL.IS","FROTO.IS",
        "GARAN.IS","KCHOL.IS","KOZAL.IS","PETKM.IS","SAHOL.IS",
        "SISE.IS","TCELL.IS","THYAO.IS","TOASO.IS","TUPRS.IS"
    ]

    results = []

    for symbol in bist_stocks:

        try:

            print("Hisse taranıyor:", symbol)

            data = yf.download(symbol, period="6mo", progress=False)

            if data is None or data.empty:
                continue

            close = data["Close"]
            volume = data["Volume"]

            # DataFrame -> Series dönüşümü
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]

            if isinstance(volume, pd.DataFrame):
                volume = volume.iloc[:, 0]

            close = pd.to_numeric(close, errors="coerce").dropna()
            volume = pd.to_numeric(volume, errors="coerce").dropna()

            if len(close) < 60:
                continue

            price = float(close.iloc[-1])

            score = score_stock(data)

            if score is None:
                continue

            # AI filtre
            if score >= 70:

                results.append({
                    "symbol": symbol,
                    "price": price,
                    "score": score
                })

        except Exception as e:

            print("Scanner hata verdi:", e)

    # Sonuçlar
    if len(results) == 0:

        print("Radar sonucu bulunamadı.")
        return

    print("Radar sonuçları:")

    message = "🚀 BIST AI RADAR\n\n"

    for r in results:

        line = f"{r['symbol']}\nAI Score: {r['score']}\nPrice: {round(r['price'],2)}\n\n"

        print(line)

        message += line

    # Telegram gönder
    try:
        send_telegram_message(message)
    except Exception as e:
        print("Telegram gönderim hatası:", e)

    print("Radar tamamlandı.")
