import time

# Bellekte sinyaller tutulur
signal_memory = {}

# kaç dakika tekrar göndermesin
MEMORY_MINUTES = 30


def is_new_signal(symbol):

    now = time.time()

    if symbol not in signal_memory:
        signal_memory[symbol] = now
        return True

    last_time = signal_memory[symbol]

    if (now - last_time) > MEMORY_MINUTES * 60:

        signal_memory[symbol] = now
        return True

    return False
