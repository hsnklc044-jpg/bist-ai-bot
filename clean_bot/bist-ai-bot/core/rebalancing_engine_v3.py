import pandas as pd


def generate_rebalance_report_v3():

    try:

        current_df = pd.read_csv(
            "data/portfolio.csv"
        )

        model_df = pd.read_csv(
            "data/portfolio_model.csv"
        )

        current_symbols = set(
            current_df[
                current_df["status"] == "OPEN"
            ]["symbol"]
        )

        model_symbols = set(
            model_df["symbol"]
        )

        sell_symbols = sorted(
            current_symbols - model_symbols
        )

        buy_symbols = sorted(
            model_symbols - current_symbols
        )

        keep_symbols = sorted(
            current_symbols & model_symbols
        )

        report = (
            "🔄 REBALANCE REPORT\n\n"
        )

        report += (
            "🔴 SELL ALL\n\n"
        )

        if sell_symbols:

            for symbol in sell_symbols:

                report += (
                    f"{symbol}\n"
                )

        else:

            report += (
                "No positions.\n"
            )

        report += "\n"

        report += (
            "🟢 KEEP\n\n"
        )

        if keep_symbols:

            for symbol in keep_symbols:

                report += (
                    f"{symbol}\n"
                )

        else:

            report += (
                "No positions.\n"
            )

        report += "\n"

        report += (
            "🟡 BUY\n\n"
        )

        if buy_symbols:

            for symbol in buy_symbols:

                report += (
                    f"{symbol}\n"
                )

        else:

            report += (
                "No positions.\n"
            )

        return report

    except Exception as e:

        return (
            f"REBALANCE V3 ERROR\n\n{e}"
        )