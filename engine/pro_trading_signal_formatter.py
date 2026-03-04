def format_signal(signal):

    text = f"""
🚀 <b>ULTIMATE TRADE SIGNAL</b>

📈 <b>Hisse:</b> {signal["symbol"]}
💰 <b>Fiyat:</b> {signal["price"]}

🧠 <b>AI Score:</b> {signal["ai_score"]}/100

🎯 <b>Entry:</b> {signal["entry"]}
🚀 <b>Target:</b> {signal["target"]}
🛑 <b>Stop:</b> {signal["stop"]}

⚖️ <b>Risk/Reward:</b> {round(signal["rr"],2)}
"""

    if signal["trend"]:
        text += "\n📈 Trend Detected"

    if signal["relative_strength"]:
        text += "\n📊 Relative Strength"

    if signal["volume_spike"]:
        text += "\n⚡ Volume Spike"

    if signal["volume_anomaly"]:
        text += "\n🔥 Volume Anomaly"

    if signal["institutional"]:
        text += "\n💰 Institutional Activity"

    return text
