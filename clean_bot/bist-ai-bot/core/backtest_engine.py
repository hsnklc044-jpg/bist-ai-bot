import yfinance as yf
import pandas as pd


def run_backtest(
    symbol="EREGL.IS",
    hold_days=10
):

    try:

        df = yf.download(
            symbol,
            period="1y",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if df.empty:
            return "No data."

        if isinstance(
            df.columns,
            pd.MultiIndex
        ):

            close = (
                df["Close"]
                .iloc[:, 0]
            )

        else:

            close = df["Close"]

        df = pd.DataFrame({
            "close": close
        })

        df["ma20"] = (
            df["close"]
            .rolling(20)
            .mean()
        )

        df["ma50"] = (
            df["close"]
            .rolling(50)
            .mean()
        )

        trades = []

        for i in range(
            60,
            len(df) - hold_days
        ):

            ma20 = (
                df["ma20"]
                .iloc[i]
            )

            ma50 = (
                df["ma50"]
                .iloc[i]
            )

            if (
                pd.isna(ma20)
                or pd.isna(ma50)
            ):
                continue

            if ma20 > ma50:

                entry_price = (
                    df["close"]
                    .iloc[i]
                )

                exit_price = (
                    df["close"]
                    .iloc[i + hold_days]
                )

                pnl = round(

                    (
                        exit_price
                        - entry_price
                    )
                    / entry_price
                    * 100,

                    2
                )

                trades.append(
                    pnl
                )

        if len(trades) == 0:

            return (
                "BACKTEST REPORT\n\n"
                "No trades found."
            )

        winners = len(
            [
                x
                for x in trades
                if x > 0
            ]
        )

        losers = len(
            [
                x
                for x in trades
                if x <= 0
            ]
        )

        win_rate = round(

            winners
            / len(trades)
            * 100,

            2
        )

        avg_return = round(

            sum(trades)
            / len(trades),

            2
        )

        report = (

            "📊 BACKTEST REPORT\n\n"

            f"Symbol : {symbol}\n\n"

            f"Hold Days : "
            f"{hold_days}\n\n"

            f"Trades : "
            f"{len(trades)}\n\n"

            f"Winners : "
            f"{winners}\n"

            f"Losers : "
            f"{losers}\n\n"

            f"Win Rate : "
            f"{win_rate}%\n\n"

            f"Average Return : "
            f"{avg_return}%\n\n"

            f"Best Trade : "
            f"{max(trades)}%\n"

            f"Worst Trade : "
            f"{min(trades)}%"
        )

        return report

    except Exception as e:

        return (
            "BACKTEST ERROR\n\n"
            f"{e}"
        )