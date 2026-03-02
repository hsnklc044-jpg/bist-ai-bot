# performance_tracker.py

from trade_engine import (
    get_winrate,
    get_avg_r,
    get_drawdown,
    get_kelly_multiplier,
)


def get_bayesian_winrate():
    return get_winrate()


def calculate_drawdown():
    return get_drawdown()


def get_loss_streak():
    return 0


def get_volatility_regime():
    return "normal"


def monte_carlo_tail_risk():
    return 0.0


def detect_regime_change():
    return "stable"


def get_position_multiplier():
    return get_kelly_multiplier()
