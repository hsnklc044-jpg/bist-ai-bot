import os


def calculate_position(entry, stop):

    try:

        capital = float(os.getenv("CAPITAL", 100000))
        risk_percent = float(os.getenv("RISK_PERCENT", 1))

        risk_amount = capital * (risk_percent / 100)

        risk_per_share = abs(entry - stop)

        if risk_per_share == 0:
            return None

        position_size = risk_amount / risk_per_share

        position_size = round(position_size, 0)

        return {
            "capital": capital,
            "risk_percent": risk_percent,
            "risk_amount": round(risk_amount, 2),
            "position_size": int(position_size)
        }

    except Exception as e:

        print("Risk engine error:", e)

        return None
