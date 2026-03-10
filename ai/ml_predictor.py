from bist_data import get_price
from sklearn.linear_model import LinearRegression
import numpy as np


def predict(symbol):

    df = get_price(symbol)

    if df is None or len(df) < 60:
        return "Veri yetersiz."

    closes = df["Close"].values

    X = []
    y = []

    for i in range(5, len(closes)-1):

        X.append(closes[i-5:i])
        y.append(closes[i])

    X = np.array(X)
    y = np.array(y)

    model = LinearRegression()
    model.fit(X, y)

    last = closes[-5:]

    prediction = model.predict([last])[0]

    current = closes[-1]

    change = (prediction - current) / current * 100

    direction = "⬆️ YUKARI" if change > 0 else "⬇️ AŞAĞI"

    msg = f"""
🤖 AI Price Prediction

Hisse: {symbol}

Tahmin: {direction}

Beklenen Değişim: %{round(change,2)}
"""

    return msg