from portfolio_system.pnl_engine import PNLEngine
from portfolio_system.portfolio_manager import PortfolioManager
from risk.exit_manager import ExitManager
from tg.notifier import TelegramNotifier

from config import TOKEN, CHAT_ID


pnl_engine = PNLEngine()

portfolio = PortfolioManager()

exit_manager = ExitManager()

notifier = TelegramNotifier(
    TOKEN,
    CHAT_ID
)

results = pnl_engine.calculate()

for trade in results:

    symbol = trade["symbol"]

    signal = trade["signal"]

    entry_price = trade["entry_price"]

    current_price = trade["current_price"]

    pnl = trade["pnl_percent"]

    atr = portfolio.positions[symbol]["atr"]

    exit_check = exit_manager.check_exit(

        signal,
        entry_price,
        current_price,
        atr
    )

    if exit_check["exit"]:

        reason = exit_check["reason"]

        message = (

            f"🚨 POSITION CLOSED\n\n"

            f"Symbol: {symbol}\n"

            f"Reason: {reason}\n"

            f"PnL %: {pnl}"
        )

        print(message)

        notifier.notify(message)

        portfolio.remove_position(symbol)

    else:

        print(
            f"[OPEN] {symbol} -> "
            f"{pnl}%"
        )