def extract_regime_features(data):

    close = data["Close"]

    ma20 = close.rolling(20).mean().iloc[-1]
    ma50 = close.rolling(50).mean().iloc[-1]

    price = close.iloc[-1]

    trend = price - ma50

    volatility = close.pct_change().std()

    return [
        price,
        ma20,
        ma50,
        trend,
        volatility
    ]
