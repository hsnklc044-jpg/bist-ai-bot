def calculate_position_size(signal):

    try:

        ai_score = signal["ai_score"]
        rr = signal["rr"]

        # confidence
        confidence = min(int(ai_score * 0.9), 95)

        # risk seviyesi
        if rr >= 2.5:
            risk = "LOW"
        elif rr >= 1.8:
            risk = "MEDIUM"
        else:
            risk = "HIGH"

        # pozisyon büyüklüğü
        if ai_score >= 85:
            position = 10
        elif ai_score >= 75:
            position = 8
        elif ai_score >= 65:
            position = 6
        else:
            position = 4

        return {
            "position": position,
            "risk": risk,
            "confidence": confidence
        }

    except Exception as e:

        print("Position sizing error:", e)

        return {
            "position": 5,
            "risk": "MEDIUM",
            "confidence": 50
        }def calculate_position_size(signal):

    try:

        ai_score = signal["ai_score"]
        rr = signal["rr"]

        # confidence
        confidence = min(int(ai_score * 0.9), 95)

        # risk seviyesi
        if rr >= 2.5:
            risk = "LOW"
        elif rr >= 1.8:
            risk = "MEDIUM"
        else:
            risk = "HIGH"

        # pozisyon büyüklüğü
        if ai_score >= 85:
            position = 10
        elif ai_score >= 75:
            position = 8
        elif ai_score >= 65:
            position = 6
        else:
            position = 4

        return {
            "position": position,
            "risk": risk,
            "confidence": confidence
        }

    except Exception as e:

        print("Position sizing error:", e)

        return {
            "position": 5,
            "risk": "MEDIUM",
            "confidence": 50
        }
