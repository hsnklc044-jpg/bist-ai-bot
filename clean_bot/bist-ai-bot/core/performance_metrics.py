import pandas as pd


def generate_performance_metrics():

    df = pd.read_csv(
        "data/equity_curve.csv"
    )

    equity = df["equity"]

    initial = equity.iloc[0]
    final = equity.iloc[-1]

    total_return = (
        (final - initial)
        / initial
        * 100
    )

    running_max = equity.cummax()

    drawdown = (
        (equity - running_max)
        / running_max
        * 100
    )

    max_drawdown = abs(
        round(drawdown.min(), 2)
    )

    returns = equity.pct_change().dropna()

    sharpe = 0

    if returns.std() != 0:

        sharpe = round(
            (
                returns.mean()
                /
                returns.std()
            )
            *
            (252 ** 0.5),
            2
        )

    profit_factor = round(
        final / initial,
        2
    )

    win_rate = round(
        (
            len(
                returns[
                    returns > 0
                ]
            )
            /
            len(returns)
        )
        * 100,
        2
    )

    report = f"""

📊 QUANTBIST METRICS

💰 Total Return : {round(total_return,2)}%

📉 Max Drawdown : {max_drawdown}%

⚡ Sharpe Ratio : {sharpe}

🏆 Profit Factor : {profit_factor}

🎯 Win Rate : {win_rate}%

"""

    return report