from radar_engine import run_radar
from breakout_engine import find_breakouts
from volume_radar import find_volume_spikes
from smart_money_radar import find_smart_money
from whale_radar import find_whales
from radar_engine import symbols


def multi_signal():

    signals = {}

    try:

        radar = run_radar()

        for s, score in radar:
            signals[s] = signals.get(s, 0) + 1

    except:
        pass

    try:

        for s in find_breakouts(symbols):
            signals[s] = signals.get(s, 0) + 1

    except:
        pass

    try:

        for s in find_volume_spikes(symbols):
            signals[s] = signals.get(s, 0) + 1

    except:
        pass

    try:

        for s in find_smart_money(symbols):
            signals[s] = signals.get(s, 0) + 1

    except:
        pass

    try:

        for s in find_whales(symbols):
            signals[s] = signals.get(s, 0) + 1

    except:
        pass

    sorted_signals = sorted(signals.items(), key=lambda x: x[1], reverse=True)

    return sorted_signals[:5]
