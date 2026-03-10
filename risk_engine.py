def calculate_risk(symbol, entry, stop, capital=100000, risk_percent=2):

    try:

        entry = float(entry)
        stop = float(stop)

        risk_per_share = abs(entry - stop)

        if risk_per_share == 0:
            return None

        max_risk = capital * (risk_percent / 100)

        position_size = max_risk / risk_per_share

        return {
            "symbol": symbol,
            "entry": entry,
            "stop": stop,
            "risk_per_share": round(risk_per_share,2),
            "position_size": int(position_size),
            "max_risk": int(max_risk),
            "risk_percent": risk_percent
        }

    except:

        return None