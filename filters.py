# filters.py

def classify(score):

    if score >= 85:
        return "🔥 KURUMSAL GÜÇLÜ AL"
    elif score >= 75:
        return "🟢 STRONG BUY"
    elif score >= 65:
        return "👶 ERKEN TREND"
    else:
        return None
