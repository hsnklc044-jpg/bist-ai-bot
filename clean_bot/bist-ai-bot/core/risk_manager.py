def calculate_position_size(

    portfolio_size,
    risk_percent,
    entry_price,
    stop_price

):

    try:

        max_risk = (
            portfolio_size
            * risk_percent
            / 100
        )

        risk_per_share = abs(
            entry_price
            - stop_price
        )

        if risk_per_share <= 0:

            return (
                "Invalid Stop Loss"
            )

        quantity = int(
            max_risk
            / risk_per_share
        )

        position_value = round(
            quantity
            * entry_price,
            2
        )

        return (

            "💰 POSITION SIZING\n\n"

            f"Portfolio : "
            f"{portfolio_size} TL\n\n"

            f"Risk : "
            f"%{risk_percent}\n\n"

            f"Max Risk : "
            f"{round(max_risk,2)} TL\n\n"

            f"Risk Per Share : "
            f"{round(risk_per_share,2)} TL\n\n"

            f"Lot : "
            f"{quantity}\n\n"

            f"Position Value : "
            f"{position_value} TL"
        )

    except Exception as e:

        return (
            f"RISK ERROR\n{e}"
        )