import pandas as pd
import yfinance as yf

from core.score_engine import calculate_score


def validate_risk(symbol="EREGL.IS"):

    try:

        df = yf.download(
            symbol,
            period="1y",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):

            close = df["Close"].iloc[:, 0]
            high = df["High"].iloc[:, 0]
            low = df["Low"].iloc[:, 0]
            volume = df["Volume"].iloc[:, 0]

        else:

            close = df["Close"]
            high = df["High"]
            low = df["Low"]
            volume = df["Volume"]

        capital = 10000

        equity_curve = [capital]

        i = 60

        while i < len(close) - 10:

            score = calculate_score(
                close.iloc[:i + 1],
                high.iloc[:i + 1],
                low.iloc[:i + 1],
                volume.iloc[:i + 1]
            )

            if score is None or score < 70:

                i += 1
                continue

            entry = float(close.iloc[i])

            stop_price = entry * 0.95

            exit_price = None
            exit_index = i + 10

            for j in range(
                i + 1,
                min(i + 11, len(close))
            ):

                if float(low.iloc[j]) <= stop_price:

                    exit_price = stop_price
                    exit_index = j
                    break

            if exit_price is None:

                exit_price = float(
                    close.iloc[i + 10]
                )

            pnl = (
                (exit_price - entry)
                / entry
                * 100
            )

            capital *= (
                1 + pnl / 100
            )

            equity_curve.append(
                capital
            )

            i = exit_index + 1

        peak = equity_curve[0]

        max_drawdown = 0

        for equity in equity_curve:

            if equity > peak:

                peak = equity

            dd = (
                (peak - equity)
                / peak
                * 100
            )

            if dd > max_drawdown:

                max_drawdown = dd

        total_return = round(
            (
                capital - 10000
            )
            / 10000
            * 100,
            2
        )

        risk_score = round(
            total_return
            / max(max_drawdown, 1),
            2
        )

        return {
            "symbol": symbol,
            "return": total_return,
            "drawdown": round(
                max_drawdown,
                2
            ),
            "risk_score": risk_score
        }

    except Exception:

        return None