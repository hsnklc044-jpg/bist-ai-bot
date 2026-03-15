import json
from logger_engine import log_info
from data_engine import get_price

FILE = "trades.json"


def track_trades():

    try:

        with open(FILE, "r") as f:
            trades = json.load(f)

    except:
        return "Trade verisi bulunamadı."

    results = []

    for trade in trades:

        symbol = trade["symbol"]

        entry_price = trade["price"]

        current_price = get_price(symbol)

        if current_price is None:
            continue

        change = ((current_price - entry_price) / entry_price) * 100

        results.append((symbol, round(change, 2)))

    if not results:
        return "Trade takibi yapılamadı."

    message = "📊 TRADE TAKİP RAPORU\n\n"

    for symbol, change in results:

        message += f"{symbol} → %{change}\n"

    log_info("Trade tracker report generated")

    return message
