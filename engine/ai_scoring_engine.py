import pandas as pd


def _to_series(col):
    """
    yfinance bazen MultiIndex/DataFrame döndürür.
    Bu fonksiyon Close/Volume'u tek Series'e indirger.
    """
    if isinstance(col, pd.DataFrame):
        # ilk kolonu al
        col = col.iloc[:, 0]
    return pd.to_numeric(col, errors="coerce")


def score_stock(df):

    try:

        close = _to_series(df["Close"]).dropna()
        volume = _to_series(df["Volume"]).dropna()

        if len(close) < 50:
            return None

        price = close.iloc[-1]

        ma20 = close.rolling(20).mean().iloc[-1]
        ma50 = close.rolling(50).mean().iloc[-1]

        score = 50

        # trend
        if price > ma20:
            score += 10

        if price > ma50:
            score += 10

        if ma20 > ma50:
            score += 10

        # momentum
        momentum = close.pct_change(10).iloc[-1]
        if pd.notna(momentum) and momentum > 0.05:
            score += 10

        # volume spike
        if volume.iloc[-1] > volume.mean():
            score += 10

        return int(score)

    except Exception as e:
        print("AI scoring hata:", e)
        return None
