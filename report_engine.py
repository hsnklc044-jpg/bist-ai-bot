import json
from logger_engine import log_info

FILE = "trades.json"


def generate_daily_report():

    try:

        with open(FILE, "r") as f:
            trades = json.load(f)

    except:

        return "Rapor oluşturulamadı."

    if not trades:
        return "Trade verisi bulunamadı."

    total_signals = len(trades)

    rsi_values = []

    symbols = set()

    for trade in trades:

        symbols.add(trade["symbol"])

        if "rsi" in trade:
            rsi_values.append(trade["rsi"])

    avg_rsi = 0

    if rsi_values:
        avg_rsi = round(sum(rsi_values) / len(rsi_values), 2)

    report = (
        "📊 GÜNLÜK RAPOR\n\n"
        f"Toplam sinyal: {total_signals}\n"
        f"Takip edilen hisseler: {len(symbols)}\n"
        f"Ortalama RSI: {avg_rsi}\n"
    )

    log_info("Daily report generated")

    return report
