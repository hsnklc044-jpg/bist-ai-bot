def allocate_portfolio_v2(capital=100000):

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

    filtered = {}

    for symbol, score in assets.items():

        if score >= 5:

            filtered[symbol] = score

    total_score = sum(
        filtered.values()
    )

    report = (
        "🚀 PORTFOLIO ALLOCATION V2\n\n"
    )

    total_allocated = 0

    for symbol, score in filtered.items():

        weight = round(
            score / total_score * 100,
            2
        )

        amount = round(
            capital * weight / 100,
            2
        )

        total_allocated += amount

        report += (

            f"{symbol}\n"

            f"Weight : {weight}%\n"

            f"Capital : {amount} TL\n\n"
        )

    report += (
        f"Total Allocated : "
        f"{round(total_allocated,2)} TL"
    )

    return report