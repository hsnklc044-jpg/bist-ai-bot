from opportunity_score import opportunity_score
from signal_sorter import sort_signals


def rank_opportunities(signals):

    ranked = []

    for s in signals:

        score = opportunity_score(s)

        s["opportunity"] = score

        ranked.append(s)

    ranked = sort_signals(ranked)

    return ranked[:5]
