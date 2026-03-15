# market_data.py

import random
import pandas as pd

def generate_price_series(length=50):
"""
Basit fiyat serisi üretir (simülasyon).
Gerçek veri bağlanana kadar kullanılacak.
"""
price = random.uniform(50, 200)
prices = []

```
for _ in range(length):
    change = random.uniform(-2, 2)
    price = max(price + change, 1)
    prices.append(round(price, 2))

return pd.Series(prices)
```

def calculate_rsi(series, period=14):
delta = series.diff()

```
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

avg_gain = gain.rolling(period).mean()
avg_loss = loss.rolling(period).mean()

rs = avg_gain / avg_loss
rsi = 100 - (100 / (1 + rs))

return round(rsi.iloc[-1], 2)
```

def calculate_ema(series, period=20):
