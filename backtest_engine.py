import yfinance as yf
from ta.momentum import RSIIndicator


def run_backtest(symbol):

    try:

        data = yf.download(symbol, period="5y", progress=False)

        wins = 0
        losses = 0

        for i in range(30, len(data) - 5):

            window = data.iloc[:i]

            rsi = RSIIndicator(window["Close"]).rsi().iloc[-1]

            if rsi < 35:

                entry = data["Close"].iloc[i]
                exit_price = data["Close"].iloc[i + 5]

                if exit_price > entry:
                    wins += 1
                else:
                    losses += 1

        total = wins + losses

        if total == 0:
            return {
                "win_rate": 0,
                "trades": 0
            }

        win_rate = (wins / total) * 100

        return {
            "win_rate": round(win_rate,2),
            "trades": total
        }

    except:

        return {
            "win_rate": 0,
            "trades": 0
        }
