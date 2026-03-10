import yfinance as yf
from bist_symbols import bist_symbols


def run_backtest():

    wins = 0
    losses = 0
    trades = 0

    for symbol in bist_symbols:

        try:

            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1y")

            if df.empty or len(df) < 60:
                continue

            ma20 = df["Close"].rolling(20).mean()
            ma50 = df["Close"].rolling(50).mean()

            for i in range(50, len(df)-5):

                # sinyal
                if ma20.iloc[i] > ma50.iloc[i]:

                    entry = df["Close"].iloc[i]
                    exit_price = df["Close"].iloc[i+5]

                    trades += 1

                    if exit_price > entry:
                        wins += 1
                    else:
                        losses += 1

        except Exception as e:

            print("Backtest error:", symbol, e)

    if trades == 0:
        return None

    win_rate = (wins / trades) * 100

    profit_factor = wins / losses if losses > 0 else wins

    return {
        "trades": trades,
        "win_rate": round(win_rate,2),
        "profit_factor": round(profit_factor,2)
    }