import yfinance as yf
import time

from engine.ai_scoring_engine import ai_score
from engine.market_regime_engine import get_market_regime
from engine.bist100 import get_bist100_tickers
from engine.smart_entry_engine import detect_entry
from engine.noise_filter_engine import noise_filter
from engine.multi_timeframe_engine import multi_tf_trend
from engine.liquidity_engine import liquidity_score
from engine.orderflow_engine import orderflow_score
from engine.volatility_engine import volatility_score
from engine.smart_money_engine import smart_money_score
from engine.confidence_engine import confidence_score
from engine.risk_engine import risk_levels


def get_data(ticker):

    try:

        stock = yf.Ticker(ticker)

        data = stock.history(
            period="5d",
            interval="1h"
        )

        if data is None or data.empty:
            return None

        return data

    except Exception as e:

        print("Data error:", ticker, e)

        return None


def ultimate_scanner():

    regime = get_market_regime()

    if regime == "BEAR":

        print("📉 Piyasa düşüş trendinde radar durduruldu")

        return []

    tickers = get_bist100_tickers()

    signals = []

    for ticker in tickers:

        try:

            print("Hisse taranıyor:", ticker)

            # Multi timeframe trend
            if not multi_tf_trend(ticker):
                continue

            data = get_data(ticker)

            if data is None:

                print("⚠ Veri alınamadı:", ticker)

                continue

            close = data["Close"]
            volume = data["Volume"]
            low = data["Low"]
            high = data["High"]

            last_price = float(close.iloc[-1])

            # Noise filter
            if not noise_filter(close, volume):
                continue

            # AI score
            score = ai_score(close, volume)

            score += liquidity_score(volume)

            score += orderflow_score(close, volume)

            score += volatility_score(close, high, low)

            score += smart_money_score(close, volume)

            if score < 8:
                continue

            # Entry setup
            entry_type = detect_entry(close, high, low)

            if entry_type is None:
                continue

            # Support
            support = float(low.tail(20).min())

            entry = round(support * 1.01, 2)

            # ATR Risk Engine
            risk = risk_levels(entry, high, low, close)

            if risk is None:
                continue

            stop, target = risk

            confidence = confidence_score(score)

            signals.append({

                "ticker": ticker,
                "price": round(last_price, 2),
                "support": round(support, 2),
                "entry": entry,
                "stop": stop,
                "target": target,
                "score": score,
                "confidence": confidence,
                "setup": entry_type

            })

            time.sleep(1)

        except Exception as e:

            print("Scanner error:", ticker, e)

    signals = sorted(signals, key=lambda x: x["score"], reverse=True)

    results = []

    for s in signals[:3]:

        message = (

            f"🚀 {s['ticker']}\n"
            f"Setup: {s['setup']}\n"
            f"Fiyat: {s['price']}\n"
            f"Destek: {s['support']}\n"
            f"Alım: {s['entry']}\n"
            f"Stop: {s['stop']}\n"
            f"Hedef: {s['target']}\n"
            f"AI Skor: {s['score']}/10\n"
            f"Güven: %{s['confidence']}"

        )

        results.append(message)

    return results


def run_ultimate_scanner():

    print("📡 BIST AI radar çalışıyor...")

    results = ultimate_scanner()

    if not results:

        print("Radar sinyal bulamadı")

    else:

        print("Sinyaller bulundu")

        for r in results:

            print(r)

    return results
