import pandas as pd
import yfinance as yf


def generate_portfolio_report():

    try:

        df = pd.read_csv(
            "data/portfolio.csv"
        )

        if df.empty:

            return "💼 Portföy boş"

        report = "💼 PORTFOLIO\n\n"

        open_count = 0

        winners = 0
        losers = 0

        total_pnl = 0

        best_symbol = ""
        best_pnl = -999

        worst_symbol = ""
        worst_pnl = 999

        for _, row in df.iterrows():

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

                entry_price = float(
                    row["entry"]
                )

                pnl = round(
                    (
                        (
                            current_price
                            - entry_price
                        )
                        / entry_price
                    ) * 100,
                    2
                )

                total_pnl += pnl

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

                    f"{symbol}\n"

                    f"Entry : {entry_price}\n"

                    f"Current : "
                    f"{round(current_price,2)}\n\n"

                    f"PnL : {pnl}%\n\n"

                    f"Status : "
                    f"{row['status']}\n\n"
                )

            except Exception:

                continue

            if row["status"] == "OPEN":

                open_count += 1

        average_pnl = round(
            total_pnl / len(df),
            2
        )

        report += (

            "━━━━━━━━━━━━━━\n\n"

            f"📈 Winners : {winners}\n"
            f"📉 Losers : {losers}\n\n"

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