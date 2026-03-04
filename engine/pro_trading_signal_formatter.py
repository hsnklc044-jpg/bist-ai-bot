def format_signal(signal):

    symbol = signal["symbol"]
    score = signal["score"]

    entry = signal["entry"]
    target = signal["target"]
    stop = signal["stop"]
    rr = signal["rr"]

    rs = signal["relative_strength"]
    vol = signal["volume_spike"]
    inst = signal["institutional"]
    squeeze = signal["squeeze"]

    tags = []

    if rs:
        tags.append("📊 Relative Strength")

    if vol:
        tags.append("⚡ Volume Spike")

    if inst:
        tags.append("💰 Institutional Flow")

    if squeeze:
        tags.append("🔥 Volatility Squeeze")

    tag_text = "\n".join(tags)

    message = f"""
🚀 ULTIMATE TRADE SIGNAL

📈 Hisse: {symbol}
🧠 AI Score: {score}

🎯 Entry: {entry}
🚀 Target: {target}
🛑 Stop: {stop}

⚖️ Risk/Reward: {rr}

{tag_text}
"""

    return message.strip()
