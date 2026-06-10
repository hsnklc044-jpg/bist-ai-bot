import yfinance as yf
import pandas as pd


def run_backtest_v2(symbol="EREGL.IS"):

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
            volume = df["Volume"].iloc[:, 0]

        else:

            close = df["Close"]
            volume = df["Volume"]

        trades = []

        for i in range(60, len(close) - 10):

            history = close.iloc[:i+1]

            ma20 = history.rolling(20).mean().iloc[-1]
            ma50 = history.rolling(50).mean().iloc[-1]

            delta = history.diff()

            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)

            avg_gain = gain.rolling(14).mean().iloc[-1]
            avg_loss = loss.rolling(14).mean().iloc[-1]

            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            ema12 = history.ewm(
                span=12,
                adjust=False
            ).mean()

            ema26 = history.ewm(
                span=26,
                adjust=False
            ).mean()

            macd = ema12.iloc[-1] - ema26.iloc[-1]

            avg_vol = volume.iloc[:i+1].rolling(20).mean().iloc[-1]

            if avg_vol > 0:
                volume_ratio = (
                    volume.iloc[i]
                    / avg_vol
                )
            else:
                volume_ratio = 1

            bull_score = 0

            if ma20 > ma50:
                bull_score += 25

            if rsi < 40:
                bull_score += 10

            if macd > 0:
                bull_score += 15

            if volume_ratio > 1.1:
                bull_score += 10

            score = 50 + (bull_score * 0.5)

            if score < 70:
                continue

            entry = close.iloc[i]
            exit_price = close.iloc[i + 10]

            pnl = round(
                (
                    exit_price - entry
                )
                / entry
                * 100,
                2
            )

            trades.append(pnl)

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

        return (
            f"AI BACKTEST V2\n\n"
            f"Symbol : {symbol}\n\n"
            f"Trades : {len(trades)}\n"
            f"Winners : {winners}\n"
            f"Losers : {losers}\n\n"
            f"Win Rate : {win_rate}%\n\n"
            f"Average Return : {avg_return}%\n\n"
            f"Best Trade : {max(trades)}%\n"
            f"Worst Trade : {min(trades)}%"
        )

    except Exception as e:

        return f"BACKTEST ERROR\n{e}"