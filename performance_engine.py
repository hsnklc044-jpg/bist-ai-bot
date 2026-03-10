from journal_engine import get_journal


def analyze_performance():

    trades = get_journal()

    if not trades:
        return None

    total = len(trades)

    high_conf = 0
    total_conf = 0

    for t in trades:

        conf = t["confidence"]

        total_conf += conf

        if conf > 70:
            high_conf += 1

    win_rate = int((high_conf / total) * 100)

    avg_conf = int(total_conf / total)

    return {
        "trades": total,
        "win_rate": win_rate,
        "avg_conf": avg_conf
    }