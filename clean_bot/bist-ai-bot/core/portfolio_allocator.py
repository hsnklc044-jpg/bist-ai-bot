def allocate_portfolio(capital=100000):

    assets = {

        "EREGL.IS": 28.69,
        "AKBNK.IS": 17.47,
        "SISE.IS": 17.28,
        "ASELS.IS": 16.73,
        "TUPRS.IS": 10.89,
        "BIMAS.IS": 10.76,
        "THYAO.IS": 0.16,
        "GARAN.IS": -8.34
    }

    positive_assets = {
        k: v
        for k, v in assets.items()
        if v > 0
    }

    total_score = sum(
        positive_assets.values()
    )

    report = (
        "💼 PORTFOLIO ALLOCATION\n\n"
    )

    for symbol, score in positive_assets.items():

        weight = round(
            score
            / total_score
            * 100,
            2
        )

        amount = round(
            capital
            * weight
            / 100,
            2
        )

        report += (

            f"{symbol}\n"

            f"Weight : {weight}%\n"

            f"Capital : {amount} TL\n\n"
        )

    return report