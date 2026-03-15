from fast_scanner_engine import fast_scan
from rsi_engine import scan_rsi
from volume_engine import scan_volume


def daily_ai_scan():

    message = "🔥 BIST AI Günlük Tarama\n\n"

    try:

        momentum = fast_scan()
        rsi = scan_rsi()
        volume = scan_volume()

        message += "⚡ Momentum\n"
        message += momentum + "\n\n"

        message += "📉 RSI Dipleri\n"
        message += rsi + "\n\n"

        message += "💰 Hacim Patlaması\n"
        message += volume

    except Exception as e:

        message += f"Hata: {str(e)}"

    return message