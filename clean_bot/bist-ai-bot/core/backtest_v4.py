import pandas as pd
import yfinance as yf


def run_backtest_v4(symbol="EREGL.IS"):

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

        if isinstance(df.columns, pd.MultiIndex):

            close = df["Close"].iloc[:, 0]
            low = df["Low"].iloc[:, 0]

        else:

            close = df["Close"]
            low = df["Low"]

        trades = []

        capital = 10000

        for i in range(60, len(close) - 10):

            history = close.iloc[:i + 1]

            ma20 = history.rolling(20).mean().iloc[-1]
            ma50 = history.rolling(50).mean().iloc[-1]

            if pd.isna(ma20) or pd.isna(ma50):
                continue

            if ma20 <= ma50:
                continue

            entry = float(close.iloc[i])

            stop_price = entry * 0.95

            exit_price = None

            for j in range(i + 1, min(i + 11, len(close))):

                day_low = float(low.iloc[j])

                if day_low <= stop_price:

                    exit_price = stop_price
                    break

            if exit_price is None:

                exit_price = float(
                    close.iloc[i + 10]
                )

            pnl = round(
                (
                    exit_price - entry
                )
                / entry
                * 100,
                2
            )

            capital = capital * (
                1 + pnl / 100
            )

            trades.append(
                pnl
            )

        if len(trades) == 0:

            return "No trades."

        winners = len(
            [x for x in trades if x > 0]
        )

        losers = len(
            [x for x in trades if x <= 0]
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

        return (

            "📊 BACKTEST V4\n\n"

            f"Symbol : {symbol}\n\n"

            f"Trades : {len(trades)}\n"

            f"Winners : {winners}\n"
            f"Losers : {losers}\n\n"

            f"Win Rate : {win_rate}%\n\n"

            f"Average Return : {avg_return}%\n\n"

            f"Final Capital : {final_capital} TL\n"

            f"Total Return : {total_return}%\n\n"

            f"Best Trade : {max(trades)}%\n"
            f"Worst Trade : {min(trades)}%"
        )

    except Exception as e:

        return f"BACKTEST ERROR\n{e}"