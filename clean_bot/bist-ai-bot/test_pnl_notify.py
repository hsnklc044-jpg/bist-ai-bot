from portfolio_system.pnl_engine import PNLEngine
from tg.notifier import TelegramNotifier
from config import TOKEN, CHAT_ID


pnl_engine = PNLEngine()

notifier = TelegramNotifier(
    TOKEN,
    CHAT_ID
)

results = pnl_engine.calculate()

for trade in results:

    message = (

        f"📊 OPEN POSITION\n\n"

        f"Symbol: {trade['symbol']}\n"

        f"Signal: {trade['signal']}\n"

        f"Entry: {trade['entry_price']}\n"

        f"Current: {trade['current_price']}\n"

        f"PnL %: {trade['pnl_percent']}"
    )

    print(message)

    notifier.notify(message)