def calculate_position_size(signal):

    try:

        rr = signal.get("rr", 1.5)

        if rr >= 2:
            position = 10
            risk = "LOW"
            confidence = 85

        elif rr >= 1.5:
            position = 7
            risk = "MEDIUM"
            confidence = 75

        else:
            position = 5
            risk = "HIGH"
            confidence = 65

        return {
            "position": position,
            "risk": risk,
            "confidence": confidence
        }

    except Exception as e:

        print("Position sizing error:", e)

        return {
            "position": 5,
            "risk": "HIGH",
            "confidence": 50
        }
