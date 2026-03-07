import yfinance as yf
from ta.momentum import RSIIndicator

from indicators import volume_spike, trend_filter, breakout, support_resistance
from quant_engine import ai_score
from smart_money import smart_money_flow
from bist_symbols import BIST_SYMBOLS
from momentum_engine import momentum_score
from pattern_engine import detect_pattern
from timeframe_engine import timeframe_trend
from signal_ranker import get_rank_score


def scan_market():

    signals = []

    for ticker in BIST_SYMBOLS:

        try:

            data = yf.download(ticker, period="3mo", progress=False)

            if len(data) < 30:
                continue

            rsi = RSIIndicator(data["Close"]).rsi().iloc[-1]

            vol = volume_spike(data)

            trend = trend_filter(data)

            bo = breakout(data)

            smart_money = smart_money_flow(data)

            momentum = momentum_score(data)

            pattern = detect_pattern(data)

            tf_trend = timeframe_trend(ticker)

            support, resistance = support_resistance(data)

            entry = support * 1.01
            stop = support * 0.97
            target = resistance

            risk = ((entry - stop) / entry) * 100
            reward = ((target - entry) / entry) * 100

            rank = get_rank_score(ticker.replace(".IS",""))

            score = ai_score(rsi, vol, trend, bo, smart_money, momentum)

            signals.append({
                "ticker": ticker.replace(".IS",""),
                "score": score,
                "rank": rank,
                "momentum": momentum,
                "pattern": pattern,
                "timeframe": tf_trend,
                "rsi": round(rsi,2),
                "volume_spike": round(vol,2),
                "breakout": bo,
                "smart_money": smart_money,
                "entry": round(entry,2),
                "stop": round(stop,2),
                "target": round(target,2),
                "risk": round(risk,2),
                "reward": round(reward,2)
            })

        except Exception as e:

            print("Hata:", ticker, e)

    signals = sorted(signals, key=lambda x: x["score"], reverse=True)

    return signals[:5]
