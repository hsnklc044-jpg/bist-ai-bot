from core.backtest_v6 import run_backtest_v6


def validate_all_assets():

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

    report = (
        "🚀 MULTI ASSET VALIDATION\n\n"
    )

    for symbol in symbols:

        try:

            result = run_backtest_v6(
                symbol
            )

            lines = result.split("\n")

            final_return = "N/A"

            for line in lines:

                if "Total Return" in line:

                    final_return = (
                        line
                        .replace(
                            "Total Return :",
                            ""
                        )
                        .strip()
                    )

            report += (
                f"{symbol}\n"
                f"Return : {final_return}\n\n"
            )

        except Exception as e:

            report += (
                f"{symbol}\n"
                f"ERROR : {e}\n\n"
            )

    return report