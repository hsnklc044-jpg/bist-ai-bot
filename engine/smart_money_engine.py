def smart_money_score(close, volume):

    if len(volume) < 30:
        return 0

    score = 0

    # son 5 gün ortalama hacim
    recent_vol = volume.tail(5).mean()

    # önceki 20 gün ortalama hacim
    old_vol = volume.tail(25).head(20).mean()

    # hacim patlaması
    if recent_vol > old_vol * 1.7:
        score += 2

    # fiyat yukarı yönlü mü
    momentum = close.iloc[-1] / close.iloc[-10]

    if momentum > 1.04:
        score += 2

    return score
