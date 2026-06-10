import pandas as pd
import yfinance as yf


def generate_alerts_report():

    try:

        df = pd.read_csv(
            "data/portfolio.csv"
        )

        if df.empty:

            return (
                "🚨 ACTIVE ALERTS\n\n"
                "No open positions."
            )

        report = (
            "🚨 ACTIVE ALERTS\n\n"
        )

        found_alert = False

        for _, row in df.iterrows():

            if row["status"] != "OPEN":
                continue

            symbol = row["symbol"]

            try:

                data = yf.download(
                    symbol,
                    period="5d",
                    interval="1d",
                    progress=False,
                    auto_adjust=True
                )

                if data.empty:
                    continue

                if isinstance(
                    data.columns,
                    pd.MultiIndex
                ):

                    current_price = float(
                        data["Close"]
                        .iloc[:, 0]
                        .iloc[-1]
                    )

                else:

                    current_price = float(
                        data["Close"]
                        .iloc[-1]
                    )

                stop_price = float(
                    row["stop"]
                )

                target_price = float(
                    row["target1"]
                )

                stop_distance = round(
                    (
                        current_price
                        - stop_price
                    )
                    / current_price
                    * 100,
                    2
                )

                target_distance = round(
                    (
                        target_price
                        - current_price
                    )
                    / current_price
                    * 100,
                    2
                )

                if stop_distance <= 5:

                    found_alert = True

                    report += (

                        f"⚠️ {symbol}\n\n"

                        f"Current : "
                        f"{round(current_price,2)}\n"

                        f"Stop : "
                        f"{stop_price}\n\n"

                        f"Stop'a : "
                        f"%{stop_distance} kaldı\n\n"

                        "━━━━━━━━━━━━━━\n\n"
                    )

                elif target_distance <= 10:

                    found_alert = True

                    report += (

                        f"🎯 {symbol}\n\n"

                        f"Current : "
                        f"{round(current_price,2)}\n"

                        f"Target1 : "
                        f"{target_price}\n\n"

                        f"Hedefe : "
                        f"%{target_distance} kaldı\n\n"

                        "━━━━━━━━━━━━━━\n\n"
                    )

            except Exception:
                continue

        if not found_alert:

            report += (
                "No critical alerts."
            )

        return report

    except Exception as e:

        return (
            f"🚨 ALERT ERROR\n\n{e}"
        )