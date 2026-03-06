import pandas as pd


def score_stock(df):

    try:

        close = df["Close"]
        volume = df["Volume"]

        # Eğer dataframe gelirse seriye çevir
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        if isinstance(volume, pd.DataFrame):
            volume = volume.iloc[:, 0]

        close = pd.to_numeric(close, errors="coerce")
        volume = pd.to_numeric(volume, errors="coerce")

        close = close.dropna()
        volume = volume.dropna()

        if len(close) < 50:
            return None

        price = float(close.iloc[-1])

        ma20 = float(close.rolling(20).mean().iloc[-1])
        ma50 = float(close.rolling(50).mean().iloc[-1])

        score = 50

        # Trend
        if price > ma20:
            score += 10

        if price > ma50:
            score += 10

        if ma20 > ma50:
            score += 10

        # Momentum
        momentum = close.pct_change(10).iloc[-1]

        if pd.notna(momentum) and momentum > 0.05:
            score += 10

        # Hacim
        if volume.iloc[-1] > volume.mean():
            score += 10

        return int(score)

    except Exception as e:

        print("AI scoring hata:", e)

        return None
