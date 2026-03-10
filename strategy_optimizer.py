import yfinance as yf
from ta.momentum import RSIIndicator


def test_rsi_strategy(symbol, rsi_level):

    try:

        data = yf.download(symbol, period="5y", progress=False)

        wins = 0
        losses = 0

        for i in range(30, len(data) - 5):

            window = data.iloc[:i]

            rsi = RSIIndicator(window["Close"]).rsi().iloc[-1]

            if rsi < rsi_level:

                entry = data["Close"].iloc[i]
                exit_price = data["Close"].iloc[i + 5]

                if exit_price > entry:
                    wins += 1
                else:
                    losses += 1

        total = wins + losses

        if total == 0:
            return 0

        return (wins / total) * 100

    except:

        return 0
