def format_trading_signals(signals):

    if not signals:
        return "⚠️ Güçlü sinyal bulunamadı."

    message = "🚨 BIST AI RADAR\n\n"

    for s in signals:

        symbol = s.get("symbol", "")
        price = s.get("price", "")
        score = s.get("score", "")
        signal = s.get("signal", "")

        message += f"📊 {symbol}\n"
        message += f"💰 Fiyat: {price}\n"
        message += f"📈 AI Skor: {score}\n"
        message += f"🎯 {signal}\n\n"

    return message
