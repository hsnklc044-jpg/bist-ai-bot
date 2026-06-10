import pandas as pd

from core.risk_validation import validate_risk


def export_risk_validation():

    symbols = [
        "EREGL.IS",
        "THYAO.IS",
        "TUPRS.IS",
        "ASELS.IS",
        "SISE.IS",
        "BIMAS.IS",
        "GARAN.IS",
        "AKBNK.IS"
    ]

    results = []

    for symbol in symbols:

        data = validate_risk(symbol)

        if data:

            results.append(data)

    df = pd.DataFrame(results)

    df.to_csv(
        "data/risk_validation.csv",
        index=False
    )

    return (
        "Risk validation exported:\n"
        "data/risk_validation.csv"
    )