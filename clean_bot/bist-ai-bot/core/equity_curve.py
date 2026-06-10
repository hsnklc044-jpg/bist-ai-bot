import pandas as pd


def generate_equity_curve():

    try:

        df = pd.read_csv(
            "data/backtest_results.csv"
        )

        if df.empty:

            return (
                "No backtest data."
            )

        capital = 10000

        history = []

        for _, row in df.iterrows():

            pnl = float(row["pnl"])

            capital = (
                capital
                * (1 + pnl / 100)
            )

            history.append(
                round(capital, 2)
            )

        final_capital = round(
            capital,
            2
        )

        total_return = round(
            (
                final_capital - 10000
            )
            / 10000
            * 100,
            2
        )

        max_equity = max(history)

        min_equity = min(history)

        drawdown = round(
            (
                max_equity - min_equity
            )
            / max_equity
            * 100,
            2
        )

        return (

            "📈 EQUITY REPORT\n\n"

            f"Start Capital : 10000 TL\n\n"

            f"Final Capital : "
            f"{final_capital} TL\n\n"

            f"Total Return : "
            f"{total_return}%\n\n"

            f"Max Drawdown : "
            f"{drawdown}%"
        )

    except Exception as e:

        return (
            f"EQUITY ERROR\n{e}"
        )