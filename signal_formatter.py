def format_signal(signal):

    message = f"""
📈 {signal['ticker']}

AI Score: {signal['score']}

Entry: {signal['entry']}
Stop: {signal['stop']}
Target: {signal['target']}

Risk: {signal['risk']}%
Reward: {signal['reward']}%
"""

    return message
