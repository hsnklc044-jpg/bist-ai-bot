import math
import pandas as pd
import yfinance as yf


def generate_portfolio_report():

    try:

        df = pd.read_csv(
            "data/portfolio.csv"
        )

        if df.empty:

            return "💼 Portfolio Empty"

        report = "💼 OPEN PORTFOLIO\n\n"

        open_count = 0

        winners = 0
        losers = 0

        total_pnl = 0

        best_symbol = ""
        best_pnl = float("-inf")

        worst_symbol = ""
        worst_pnl = float("inf")

        processed = 0

        for _, row in df.iterrows():

            if str(
                row["status"]
            ).upper() != "OPEN":

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

                    close_series = (
                        data["Close"]
                        .iloc[:, 0]
                        .dropna()
                    )

                else:

                    close_series = (
                        data["Close"]
                        .dropna()
                    )

                if close_series.empty:
                    continue

                current_price = float(
                    close_series.iloc[-1]
                )

                entry_price = float(
                    row["entry"]
                )

                if math.isnan(
                    current_price
                ):
                    continue

                if math.isnan(
                    entry_price
                ):
                    continue

                pnl = round(
                    (
                        current_price
                        - entry_price
                    )
                    / entry_price
                    * 100,
                    2
                )

                processed += 1

                total_pnl += pnl

                open_count += 1

                if pnl >= 0:

                    winners += 1

                else:

                    losers += 1

                if pnl > best_pnl:

                    best_pnl = pnl
                    best_symbol = symbol

                if pnl < worst_pnl:

                    worst_pnl = pnl
                    worst_symbol = symbol

                report += (

                    f"📊 {symbol}\n\n"

                    f"Entry : {entry_price}\n"

                    f"Current : "
                    f"{round(current_price, 2)}\n\n"

                    f"PnL : {pnl}%\n\n"

                    "━━━━━━━━━━━━━━\n\n"
                )

            except Exception:

                continue

        if processed == 0:

            return (
                "💼 OPEN PORTFOLIO\n\n"
                "No active positions."
            )

        average_pnl = round(
            total_pnl / processed,
            2
        )

        report += (

            f"📈 Winners : "
            f"{winners}\n"

            f"📉 Losers : "
            f"{losers}\n\n"

            f"🏆 Best Position :\n"
            f"{best_symbol} "
            f"({best_pnl}%)\n\n"

            f"⚠️ Worst Position :\n"
            f"{worst_symbol} "
            f"({worst_pnl}%)\n\n"

            f"📊 Average PnL : "
            f"{average_pnl}%\n\n"

            f"📂 Open Positions : "
            f"{open_count}"
        )

        return report

    except Exception as e:

        return (
            f"❌ PORTFOLIO ERROR\n{e}"
        )