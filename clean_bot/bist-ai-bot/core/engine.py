from core.signal_engine import SignalEngine
from tg.notifier import TelegramNotifier
from risk.risk_manager import RiskManager
from portfolio_system.portfolio_manager import PortfolioManager
from config import TOKEN, CHAT_ID


class InstitutionalEngine:

    def __init__(self):

        self.signal_engine = SignalEngine()

        self.notifier = TelegramNotifier(
            TOKEN,
            CHAT_ID
        )

        self.risk_manager = RiskManager()

        self.portfolio = PortfolioManager()

        self.symbols = [
            "EREGL.IS",
            "TUPRS.IS",
            "SISE.IS",
            "ASELS.IS",
            "THYAO.IS"
        ]

    def run(self):

        print("\n🚀 Institutional Engine Started\n")

        for symbol in self.symbols:

            try:

                result = self.signal_engine.generate(symbol)

                if result is None:
                    continue

                risk_check = self.risk_manager.validate(result)

                if not risk_check["approved"]:

                    print(
                        f"[RISK FILTERED] "
                        f"{symbol} -> "
                        f"{risk_check['reason']}"
                    )

                    continue

                if self.portfolio.has_position(symbol):

                    print(
                        f"[POSITION EXISTS] {symbol}"
                    )

                    continue

                signal = result["signal"]

                price = result["price"]

                atr = result["atr"]

                message = (
                    f"🚀 ATR SIGNAL\n\n"
                    f"Symbol: {symbol}\n"
                    f"Signal: {signal}\n"
                    f"Price: {price}\n"
                    f"ATR: {atr}"
                )

                print(message)

                self.notifier.notify(message)

                self.portfolio.add_position(
                    symbol,
                    signal,
                    price,
                    atr
                )

            except Exception as e:

                print(f"[ENGINE ERROR] {symbol} -> {e}")


if __name__ == "__main__":

    engine = InstitutionalEngine()

    engine.run()