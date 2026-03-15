from logger_engine import log_info
from strategy_engine import get_adaptive_rsi


def calculate_score(price, rsi, ema50, ema200):

    score = 0

    # adaptive RSI öğrenme sistemi
    adaptive_rsi = get_adaptive_rsi()

    # RSI dip
    if rsi < adaptive_rsi:
        score += 40

    # Trend yukarı
    if ema50 > ema200:
        score += 30

    # Fiyat trend üstünde
    if price > ema50:
        score += 20

    # ekstra RSI bonus
    if rsi < (adaptive_rsi - 2):
        score += 10

    log_info(f"Score calculated: {score}")

    return score
