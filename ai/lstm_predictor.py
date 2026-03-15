import yfinance as yf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

def predict_lstm(symbol):

    ticker = yf.Ticker(symbol + ".IS")
    data = ticker.history(period="1y")

    if len(data) < 50:
        return "Yeterli veri yok."

    prices = data["Close"].values.reshape(-1,1)

    scaler = MinMaxScaler()
    prices_scaled = scaler.fit_transform(prices)

    X = []
    y = []

    window = 20

    for i in range(window, len(prices_scaled)):
        X.append(prices_scaled[i-window:i])
        y.append(prices_scaled[i])

    X = np.array(X)
    y = np.array(y)

    model = Sequential()

    model.add(LSTM(50, return_sequences=True, input_shape=(X.shape[1],1)))
    model.add(LSTM(50))
    model.add(Dense(1))

    model.compile(
        optimizer="adam",
        loss="mean_squared_error"
    )

    model.fit(
        X,
        y,
        epochs=5,
        batch_size=16,
        verbose=0
    )

    last_data = prices_scaled[-window:]
    last_data = np.reshape(last_data, (1,window,1))

    prediction = model.predict(last_data)

    predicted_price = scaler.inverse_transform(prediction)[0][0]
    current_price = prices[-1][0]

    change = (predicted_price-current_price)/current_price*100

    direction = "⬆️ YUKARI" if change > 0 else "⬇️ AŞAĞI"

    msg = f"""
🧠 LSTM AI Prediction

Hisse: {symbol}

Tahmin: {direction}

Beklenen Değişim: %{round(change,2)}
"""

    return msg
