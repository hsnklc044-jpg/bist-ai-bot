def mega_score(score):

    # mevcut skor yaklaşık 0-15 arası
    max_possible = 15

    mega = (score / max_possible) * 100

    return round(mega, 1)
