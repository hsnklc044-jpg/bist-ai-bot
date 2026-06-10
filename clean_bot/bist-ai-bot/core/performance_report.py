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

        try:

            df = pd.read_csv(
                "data/trade_history.csv"
            )

        except Exception:

            return (
                "📈 PERFORMANCE\n\n"
                "No closed trades yet."
            )

        if df.empty:

            return (
                "📈 PERFORMANCE\n\n"
                "No closed trades yet."
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

        avg_win = 0
        avg_loss = 0

        if winners > 0:

            avg_win = round(
                winners_df["pnl"].mean(),
                2
            )

        if losers > 0:

            avg_loss = round(
                losers_df["pnl"].mean(),
                2
            )

        best_trade = (
            df.loc[
                df["pnl"].idxmax()
            ]
        )

        worst_trade = (
            df.loc[
                df["pnl"].idxmin()
            ]
        )

        report = (
            "📈 PERFORMANCE\n\n"
            f"Trades : {total_trades}\n\n"
            f"Winners : {winners}\n"
            f"Losers : {losers}\n\n"
            f"Win Rate : {win_rate}%\n\n"
            f"Average Win : {avg_win}%\n"
            f"Average Loss : {avg_loss}%\n\n"
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