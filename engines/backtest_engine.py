from bist_data import get_price
from bist_symbols import symbols
from ai_score_engine import calculate_score


def run_backtest():

    wins = 0
    losses = 0
    gains = []

    for s in symbols:

        try:

            df = get_price(s)

            if df is None or len(df) < 120:
                continue

            for i in range(50, len(df)-5):

                window = df.iloc[:i]

                score = calculate_score(window)

                if score >= 8:

                    entry = df["Close"].iloc[i]
                    exit_price = df["Close"].iloc[i+5]

                    change = (exit_price - entry) / entry

                    gains.append(change)

                    if change > 0:
                        wins += 1
                    else:
                        losses += 1

        except:
            pass

    total = wins + losses

    if total == 0:
        return "Backtest sonucu bulunamadı."

    winrate = round((wins / total) * 100, 2)
    avg_gain = round(sum(gains) / len(gains) * 100, 2)

    result = f"""
📈 AI Radar Backtest

Win Rate: %{winrate}
Average Gain: %{avg_gain}

Trades Tested: {total}
"""

    return result