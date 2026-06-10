import pandas as pd

from core.backtest_v6 import run_backtest_v6


def export_validation_results():

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

        try:

            report = run_backtest_v6(
                symbol
            )

            total_return = 0

            for line in report.split("\n"):

                if "Total Return" in line:

                    total_return = float(
                        line
                        .split(":")[1]
                        .replace("%", "")
                        .strip()
                    )

            results.append({
                "symbol": symbol,
                "return": total_return
            })

        except Exception:

            continue

    df = pd.DataFrame(results)

    df.to_csv(
        "data/validation_results.csv",
        index=False
    )

    return (
        "Validation exported:\n"
        "data/validation_results.csv"
    )