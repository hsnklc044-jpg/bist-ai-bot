import yfinance as yf
import pandas as pd

from engine.market_regime_engine import market_regime
from engine.ai_scoring_engine import score_stock
from engine.entry_engine import calculate_entry
from engine.telegram_engine import send_telegram_message
from engine.bist_universe import get_bist_universe
from engine.smart_money_engine import smart_money_signal
from engine.breakout_engine import breakout_signal
from engine.risk_engine import calculate_position
from engine.portfolio_engine import is_symbol_active, add_trade


def run_ultimate_scanner():

    print("🚀 BIST AI radar çalışıyor...")

    try:
        regime = market_regime()
    except Exception as e:
        print("Market regime error:", e)
        regime = "UNKNOWN"

    print("Market rejimi:", regime)

    bist_stocks = get_bist_universe()

    results = []

    for symbol in bist_stocks:

        try:

            if is_symbol_active(symbol):
                continue

            print("Hisse taranıyor:", symbol)

            data = yf.download(symbol, period="6mo", progress=False)

            if data is None or data.empty:
                continue

            if not smart_money_signal(data):
                continue

            if not breakout_signal(data):
                continue

            score = score_stock(data)

            if score is None:
                continue

            entry_data = calculate_entry(data)

            if entry_data is None:
                continue

            risk_data = calculate_position(
                entry_data["entry"],
                entry_data["stop"]
            )

            if risk_data is None:
                continue

            if score >= 70:

                add_trade(
                    symbol,
                    entry_data["entry"],
                    entry_data["stop"],
                    entry_data["target"]
                )

                results.append({
                    "symbol": symbol,
                    "score": score,
                    "price": entry_data["price"],
                    "support": entry_data["support"],
                    "entry": entry_data["entry"],
                    "stop": entry_data["stop"],
                    "target": entry_data["target"],
                    "position_size": risk_data["position_size"],
                    "risk_amount": risk_data["risk_amount"]
                })

        except Exception as e:

            print("Scanner hata verdi:", e)

    if len(results) == 0:

        print("Radar sonucu bulunamadı.")
        return

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    results = results[:5]

    message = "🚀 BIST AI TRADE SIGNAL\n\n🔥 TOP SIGNALS\n\n"

    for r in results:

        symbol = r["symbol"].replace(".IS","")

        line = f"""📈 {symbol}
Score: {r['score']}
Price: {r['price']}

Support: {r['support']}
Entry: {r['entry']}
Stop: {r['stop']}
Target: {r['target']}

Position Size: {r['position_size']}
Risk Amount: {r['risk_amount']}

"""

        print(line)

        message += line

    send_telegram_message(message)

    print("Radar tamamlandı.")
