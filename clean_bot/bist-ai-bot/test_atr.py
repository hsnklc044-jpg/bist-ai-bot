from core.market_data import MarketData
from strategies.atr_strategy import ATRStrategy


md = MarketData()

strategy = ATRStrategy()

df = md.get_data("EREGL.IS")

result = strategy.generate_signal(df)

print(result)