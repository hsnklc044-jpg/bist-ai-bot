import pandas as pd
import yfinance as yf


def run_backtest_v5(symbol="EREGL.IS"):

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

        capital = 10000

        trades = []

        i = 60

        while i < len(close) - 10:

            history = close.iloc[:i + 1]

            ma20 = history.rolling(20).mean().iloc[-1]
            ma50 = history.rolling(50).mean().iloc[-1]

            if pd.isna(ma20) or pd.isna(ma50):

                i += 1
                continue

            if ma20 <= ma50:

                i += 1
                continue

            entry = float(
                close.iloc[i]
            )

            stop_price = round(
                entry * 0.95,
                2
            )

            exit_price = None

            exit_index = i + 10

            for j in range(
                i + 1,
                min(
                    i + 11,
                    len(close)
                )
            ):

                if float(low.iloc[j]) <= stop_price:

                    exit_price = stop_price
                    exit_index = j
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

            capital *= (
                1 + pnl / 100
            )

            trades.append(
                pnl
            )

            # ÖNEMLİ:
            # Pozisyon kapanmadan yeni işlem açma

            i = exit_index + 1

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

        report = (

            "🚀 BACKTEST V5\n\n"

            f"Symbol : {symbol}\n\n"

            f"Trades : {len(trades)}\n\n"

            f"Winners : {winners}\n"
            f"Losers : {losers}\n\n"

            f"Win Rate : {win_rate}%\n\n"

            f"Average Return : {avg_return}%\n\n"

            f"Final Capital : "
            f"{round(capital,2)} TL\n\n"

            f"Total Return : "
            f"{round((capital-10000)/10000*100,2)}%\n\n"

            f"Best Trade : "
            f"{max(trades)}%\n"

            f"Worst Trade : "
            f"{min(trades)}%"
        )

        return report

    except Exception as e:

        return (
            f"BACKTEST V5 ERROR\n{e}"
        )