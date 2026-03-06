import yfinance as yf
import pandas as pd

from engine.market_regime_engine import market_regime
from engine.ai_scoring_engine import score_stock
from engine.entry_engine import calculate_entry
from engine.telegram_engine import send_telegram_message


def run_ultimate_scanner():

    print("🚀 BIST AI radar çalışıyor...")

    try:
        regime = market_regime()
    except Exception as e:
        print("Market regime error:", e)
        regime = "UNKNOWN"

    print("Market rejimi:", regime)

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

            score = score_stock(data)

            if score is None:
                continue

            entry_data = calculate_entry(data)

            if entry_data is None:
                continue

            if score >= 70:

                results.append({
                    "symbol": symbol,
                    "score": score,
                    "price": entry_data["price"],
                    "support": entry_data["support"],
                    "entry": entry_data["entry"],
                    "stop": entry_data["stop"],
                    "target": entry_data["target"]
                })

        except Exception as e:

            print("Scanner hata verdi:", e)

    if len(results) == 0:

        print("Radar sonucu bulunamadı.")
        return

    print("Radar sonuçları:")

    message = "🚀 BIST AI SIGNAL\n\n"

    for r in results:

        symbol = r["symbol"].replace(".IS","")

        line = f"""📈 {symbol}
Score: {r['score']}
Price: {r['price']}

Support: {r['support']}
Entry: {r['entry']}
Stop: {r['stop']}
Target: {r['target']}

"""

        print(line)

        message += line

    send_telegram_message(message)

    print("Radar tamamlandı.")
