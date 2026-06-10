import pandas as pd
import yfinance as yf


def run_backtest_v3(symbol="EREGL.IS"):

    results = []

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
        else:
            close = df["Close"]

        for i in range(60, len(close) - 10):

            history = close.iloc[:i+1]

            ma20 = history.rolling(20).mean().iloc[-1]
            ma50 = history.rolling(50).mean().iloc[-1]

            if pd.isna(ma20) or pd.isna(ma50):
                continue

            if ma20 <= ma50:
                continue

            entry = float(close.iloc[i])
            exit_price = float(close.iloc[i + 10])

            pnl = round(
                (exit_price - entry)
                / entry
                * 100,
                2
            )

            results.append({
                "date": str(close.index[i].date()),
                "entry": entry,
                "exit": exit_price,
                "pnl": pnl
            })

        report_df = pd.DataFrame(results)

        report_df.to_csv(
            "data/backtest_results.csv",
            index=False
        )

        return (
            f"BACKTEST V3\n\n"
            f"Trades: {len(report_df)}\n"
            f"File Saved:\n"
            f"data/backtest_results.csv"
        )

    except Exception as e:

        return f"ERROR\n{e}"