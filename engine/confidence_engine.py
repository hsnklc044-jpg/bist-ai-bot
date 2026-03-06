def confidence_score(score):

    # maksimum skor varsayımı
    max_score = 15

    confidence = (score / max_score) * 100

    return round(confidence, 1)
