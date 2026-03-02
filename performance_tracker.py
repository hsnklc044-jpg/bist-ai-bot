# performance_tracker.py

import math

# --------------------------------------------------
# MOCK / PLACEHOLDER METRİKLER
# (Senin gerçek sistem fonksiyonların varsa bunları sil)
# --------------------------------------------------

def get_bayesian_winrate() -> float:
    return 0.58  # örnek

def calculate_drawdown() -> float:
    return 8.5  # yüzde

def get_loss_streak() -> int:
    return 1

def get_volatility_regime() -> str:
    return "normal"  # low / normal / high

def get_avg_rr() -> float:
    return 1.6

def monte_carlo_tail_risk() -> float:
    return 0.22

def detect_regime_change() -> str:
    return "stable"


# --------------------------------------------------
# ANA FONKSİYON
# --------------------------------------------------

def get_position_multiplier() -> float:
    """
    Sistem performansına göre dinamik pozisyon çarpanı.
    """

    try:
        winrate = get_bayesian_winrate()
        drawdown = calculate_drawdown()
        streak = get_loss_streak()
        vol_regime = get_volatility_regime()

        multiplier = 1.0

        # Winrate etkisi
        if winrate > 0.60:
            multiplier += 0.2
        elif winrate < 0.45:
            multiplier -= 0.2

        # Drawdown etkisi
        if drawdown > 15:
            multiplier -= 0.3
        elif drawdown > 10:
            multiplier -= 0.15

        # Loss streak
        if streak >= 4:
            multiplier -= 0.2

        # Volatilite rejimi
        if vol_regime == "high":
            multiplier -= 0.1
        elif vol_regime == "low":
            multiplier += 0.1

        # Güvenlik limitleri
        multiplier = max(0.5, min(multiplier, 1.5))

        return round(multiplier, 2)

    except Exception:
        return 1.0
