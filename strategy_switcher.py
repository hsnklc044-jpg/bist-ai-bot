from market_regime_ai import detect_market_regime
from trend_strategy import trend_strategy
from mean_reversion_strategy import mean_reversion_strategy
from defensive_strategy import defensive_strategy


def select_strategy(signal):

    regime = detect_market_regime()

    if regime == "BULL":
        return trend_strategy(signal)

    if regime == "SIDEWAYS":
        return mean_reversion_strategy(signal)

    if regime == "BEAR":
        return defensive_strategy(signal)

    return signal
