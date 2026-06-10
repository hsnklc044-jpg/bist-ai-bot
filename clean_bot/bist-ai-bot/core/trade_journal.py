import os
import pandas as pd


def generate_trade_journal():

    try:

        if not os.path.exists(
            "data/trade_history.csv"
        ):

            return (
                "📒 TRADE JOURNAL\n\n"
                "No closed trades."
            )

        df = pd.read_csv(
            "data/trade_history.csv"
        )

        if df.empty:

            return (
                "📒 TRADE JOURNAL\n\n"
                "No closed trades."
            )

        report = (
            "📒 TRADE JOURNAL\n\n"
        )

        for _, row in df.iterrows():

            report += (

                f"📊 {row['symbol']}\n\n"

                f"Reason : {row['reason']}\n"

                f"PnL : {row['pnl']}%\n\n"

                "━━━━━━━━━━━━━━\n\n"
            )

        report += (
            f"Closed Trades : {len(df)}"
        )

        return report

    except Exception as e:

        return (
            f"❌ JOURNAL ERROR\n{e}"
        )