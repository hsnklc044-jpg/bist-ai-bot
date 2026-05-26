from core.market_data import MarketData
from strategies.atr_strategy import ATRStrategy


class SignalEngine:

    def __init__(self):

        self.market = MarketData()

        self.strategy = ATRStrategy()

    def generate(self, symbol):

        df = self.market.get_data(symbol)

        if df is None:
            return None

        result = self.strategy.generate_signal(df)

        if result is None:
            return None

        return {
            "symbol": symbol,
            "signal": result["signal"],
            "price": result["price"],
            "atr": result["atr"]
        }