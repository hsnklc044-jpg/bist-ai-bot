import requests

BOT_TOKEN = "8434925197:AAHeciNObLAkLJ_SE_jsaNPvhiwR9_HRoTE"
CHAT_ID = "1790584407"


def send_message(message):

    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:

        requests.post(
            url,
            data=payload,
            timeout=10
        )

        print(
            "[TELEGRAM] Message Sent"
        )

    except Exception as e:

        print(
            f"[TELEGRAM ERROR] {e}"
        )


def send_ai_signal(data):

    message = (
        f"🤖 AI FILTER SIGNAL\n\n"

        f"📊 Symbol : {data['symbol']}\n"
        f"🎯 Signal : {data['signal']}\n\n"

        f"🔥 AI Score : {data['score']}/100\n"
        f"⭐ Confidence : {data['confidence']}%\n\n"

        f"📈 Trend : {data['trend']}\n"
        f"📉 RSI : {data['rsi']}\n"
        f"⚡ MACD : {data['macd']}\n"
        f"📦 Volume Ratio : {data['volume_ratio']}\n"
        f"🌊 Volatility : {data['volatility']}%\n\n"

        f"💰 Entry : {data['entry_price']}\n"
        f"🛑 Stop Loss : {data['stop_loss']}\n"
        f"🎯 Target 1 : {data['target_1']}\n"
        f"🏆 Target 2 : {data['target_2']}"
    )

    send_message(message)


def send_closed_trade(result):

    message = (

        f"🚨 POSITION CLOSED\n\n"

        f"📊 Symbol : {result['symbol']}\n\n"

        f"🎯 Reason : {result['reason']}\n\n"

        f"💰 Entry : {result['entry_price']}\n"

        f"💵 Exit : {result['exit_price']}\n\n"

        f"📈 PnL : {result['pnl']}%"
    )

    send_message(message)