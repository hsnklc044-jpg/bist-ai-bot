from datetime import datetime


def bist_market_open():

    now = datetime.now()

    hour = now.hour
    minute = now.minute

    # hafta sonu kapalı
    if now.weekday() >= 5:
        return False

    current = hour * 60 + minute

    open_time = 10 * 60
    close_time = 18 * 60 + 10

    return open_time <= current <= close_time
