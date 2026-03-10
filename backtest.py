import pandas as pd
from data_service import get_data
from indicators import add_indicators


def calculate_atr(df, period=14):
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()

    return atr


def run_backtest(symbol):

    df = get_data(symbol)
    df = add_indicators(df)
    df["ATR"] = calculate_atr(df)

    df.dropna(inplace=True)

    trades = []
    in_position = False

    for i in range(50, len(df)):

        row = df.iloc[i]

        # Giriş koşulu (Ultra Quality Basit Versiyon)
        if (
            not in_position
            and row["EMA20"] > row["EMA50"]
            and row["Close"] > row["EMA20"]
            and 55 < row["RSI"] < 68
            and row["RelVolume"] > 1.3
        ):

            entry_price = row["Close"]
            atr = row["ATR"]
            stop = entry_price - (atr * 1.2)
            trend_stop = stop

            in_position = True
            entry_index = i
            continue

        if in_position:

            ema20 = row["EMA20"]
            atr = row["ATR"]

            new_trend_stop = ema20 - (atr * 0.3)
            trend_stop = max(trend_stop, new_trend_stop)

            # Çıkış koşulu
            if row["Close"] < trend_stop:

                exit_price = row["Close"]

                R = (exit_price - entry_price) / (entry_price - stop)

                trades.append(R)

                in_position = False

    return trades


if __name__ == "__main__":

    trades = run_backtest("ASELS")

    if trades:
        print("Toplam İşlem:", len(trades))
        print("Win Rate:", round(len([t for t in trades if t > 0]) / len(trades) * 100, 2), "%")
        print("Ortalama R:", round(sum(trades) / len(trades), 2))
        print("Max R:", round(max(trades), 2))
        print("Min R:", round(min(trades), 2))
    else:
        print("Hiç işlem oluşmadı.")
