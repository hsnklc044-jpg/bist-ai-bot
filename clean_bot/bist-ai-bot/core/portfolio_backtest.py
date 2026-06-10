import pandas as pd
import yfinance as yf


def run_portfolio_backtest():

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

    try:

        capital = 100000

        report = (
            "🚀 PORTFOLIO BACKTEST\n\n"
        )

        total_trades = 0

        for symbol in symbols:

            df = yf.download(
                symbol,
                period="1y",
                interval="1d",
                progress=False,
                auto_adjust=True
            )

            if df.empty:
                continue

            if isinstance(df.columns, pd.MultiIndex):

                close = df["Close"].iloc[:, 0]
                low = df["Low"].iloc[:, 0]

            else:

                close = df["Close"]
                low = df["Low"]

            symbol_capital = 10000

            trades = 0

            for i in range(
                60,
                len(close) - 10
            ):

                history = close.iloc[:i + 1]

                ma20 = (
                    history
                    .rolling(20)
                    .mean()
                    .iloc[-1]
                )

                ma50 = (
                    history
                    .rolling(50)
                    .mean()
                    .iloc[-1]
                )

                if pd.isna(ma20):
                    continue

                if pd.isna(ma50):
                    continue

                if ma20 <= ma50:
                    continue

                entry = float(
                    close.iloc[i]
                )

                stop_price = (
                    entry * 0.95
                )

                exit_price = None

                for j in range(
                    i + 1,
                    min(
                        i + 11,
                        len(close)
                    )
                ):

                    if (
                        float(low.iloc[j])
                        <= stop_price
                    ):

                        exit_price = stop_price
                        break

                if exit_price is None:

                    exit_price = float(
                        close.iloc[i + 10]
                    )

                pnl = (
                    (
                        exit_price
                        - entry
                    )
                    / entry
                    * 100
                )

                symbol_capital *= (
                    1 + pnl / 100
                )

                trades += 1

            total_trades += trades

            report += (
                f"{symbol}\n"
                f"Final : "
                f"{round(symbol_capital,2)} TL\n"
                f"Trades : {trades}\n\n"
            )

            capital += (
                symbol_capital - 10000
            )

        total_return = round(
            (
                capital - 100000
            )
            / 100000
            * 100,
            2
        )

        report += (
            "====================\n\n"
            f"Portfolio Final : "
            f"{round(capital,2)} TL\n\n"
            f"Portfolio Return : "
            f"{total_return}%\n\n"
            f"Total Trades : "
            f"{total_trades}"
        )

        return report

    except Exception as e:

        return (
            f"PORTFOLIO BACKTEST ERROR\n{e}"
        )