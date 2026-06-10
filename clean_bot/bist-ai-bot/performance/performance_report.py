import os
import pandas as pd


def generate_performance_report():

    try:

        if not os.path.exists(
            "data/trade_history.csv"
        ):

            return (
                "📈 PERFORMANCE\n\n"
                "No closed trades yet."
            )

        df = pd.read_csv(
            "data/trade_history.csv"
        )

        if df.empty:

            return (
                "📈 PERFORMANCE\n\n"
                "No closed trades yet."
            )

        df["pnl"] = pd.to_numeric(
            df["pnl"],
            errors="coerce"
        )

        total_trades = len(df)

        winners_df = df[
            df["pnl"] > 0
        ]

        losers_df = df[
            df["pnl"] <= 0
        ]

        winners = len(
            winners_df
        )

        losers = len(
            losers_df
        )

        win_rate = round(
            (winners / total_trades) * 100,
            2
        )

        total_return = round(
            df["pnl"].sum(),
            2
        )

        gross_profit = (
            winners_df["pnl"].sum()
        )

        gross_loss = abs(
            losers_df["pnl"].sum()
        )

        profit_factor = (
            round(
                gross_profit /
                gross_loss,
                2
            )
            if gross_loss > 0
            else "∞"
        )

        avg_win = round(
            winners_df["pnl"].mean(),
            2
        ) if winners > 0 else 0

        avg_loss = round(
            losers_df["pnl"].mean(),
            2
        ) if losers > 0 else 0

        best_trade = df.loc[
            df["pnl"].idxmax()
        ]

        worst_trade = df.loc[
            df["pnl"].idxmin()
        ]

        report = (

            "📈 PERFORMANCE\n\n"

            f"Trades : {total_trades}\n\n"

            f"Winners : {winners}\n"
            f"Losers : {losers}\n\n"

            f"Win Rate : {win_rate}%\n\n"

            f"Total Return : "
            f"{total_return}%\n"

            f"Profit Factor : "
            f"{profit_factor}\n\n"

            f"Average Win : "
            f"{avg_win}%\n"

            f"Average Loss : "
            f"{avg_loss}%\n\n"

            f"🏆 Best Trade\n"
            f"{best_trade['symbol']} "
            f"({best_trade['pnl']}%)\n\n"

            f"⚠️ Worst Trade\n"
            f"{worst_trade['symbol']} "
            f"({worst_trade['pnl']}%)"
        )

        return report

    except Exception as e:

        return (
            f"📈 PERFORMANCE ERROR\n"
            f"{e}"
        )