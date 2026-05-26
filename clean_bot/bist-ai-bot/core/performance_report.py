import pandas as pd


def generate_report():

    try:

        df = pd.read_csv(
            "data/portfolio.csv"
        )

        total = len(df)

        wins = len(
            df[
                df["status"].isin(
                    [
                        "TARGET1 HIT",
                        "TARGET2 HIT"
                    ]
                )
            ]
        )

        losses = len(
            df[
                df["status"] == "STOP HIT"
            ]
        )

        open_positions = len(
            df[
                df["status"] == "OPEN"
            ]
        )

        if wins + losses > 0:

            win_rate = round(
                wins /
                (wins + losses)
                * 100,
                2
            )

        else:

            win_rate = 0

        report = (

            "📊 PERFORMANCE REPORT\n\n"

            f"Total Trades : {total}\n"
            f"Wins : {wins}\n"
            f"Losses : {losses}\n"
            f"Open : {open_positions}\n"
            f"Win Rate : %{win_rate}"
        )

        return report

    except Exception as e:

        return (
            f"❌ REPORT ERROR\n{e}"
        )