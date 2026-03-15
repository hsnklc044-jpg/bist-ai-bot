from logger_engine import log_info


def calculate_position_sizes(signals):

    if not signals:
        return []

    total_score = sum(signal[0] for signal in signals)

    portfolio = []

    for signal in signals:

        score = signal[0]
        symbol = signal[1]

        weight = (score / total_score) * 100

        portfolio.append((symbol, round(weight)))

    log_info("Position sizes calculated")

    return portfolio
