from logger_engine import log_info


def rank_signals(signals):

    if not signals:
        return []

    ranked = sorted(signals, key=lambda x: x[0], reverse=True)

    log_info("Signals ranked")

    return ranked
