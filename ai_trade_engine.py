from trend_engine import get_trend
from breakout_engine import breakout_scan
from moneyflow_engine import money_flow
from scanner_engine import get_top10

def ai_trade_signals():

    signals = []

    try:
        top = get_top10()
    except:
        top = []

    for stock in top:

        score = 0

        try:
            trend = get_trend(stock)
            if trend == "UPTREND":
                score += 30
        except:
            pass

        try:
            breakout = breakout_scan(stock)
            if breakout:
                score += 30
        except:
            pass

        try:
            flow = money_flow(stock)
            if flow:
                score += 20
        except:
            pass

        if score >= 60:
            signals.append((stock, score))

    signals = sorted(signals, key=lambda x: x[1], reverse=True)

    return signals