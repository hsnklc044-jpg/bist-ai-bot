from core.ai_filter import ai_filter_stock

SYMBOLS = [
    "SASA.IS",
    "SISE.IS",
    "THYAO.IS",
    "TUPRS.IS",
    "ASELS.IS",
    "KCHOL.IS",
    "YKBNK.IS",
    "BIMAS.IS",
    "HEKTS.IS",
    "PETKM.IS",
    "TCELL.IS",
    "GARAN.IS",
    "AKBNK.IS",
    "EREGL.IS"
]


def generate_market_report():

    try:

        bullish = []
        neutral = []
        bearish = []

        for symbol in SYMBOLS:

            result = ai_filter_stock(symbol)

            if not result:
                continue

            signal = result["signal"]

            if signal in [
                "BUY",
                "STRONG BUY"
            ]:

                bullish.append(result)

            elif signal in [
                "SELL",
                "STRONG SELL"
            ]:

                bearish.append(result)

            else:

                neutral.append(result)

        if len(bullish) >= 5:

            mood = "BULLISH"

        elif len(bearish) >= 5:

            mood = "BEARISH"

        else:

            mood = "SIDEWAYS"

        top_bull = "-"

        if bullish:

            top_bull = max(
                bullish,
                key=lambda x: x["score"]
            )["symbol"]

        top_bear = "-"

        if bearish:

            top_bear = min(
                bearish,
                key=lambda x: x["score"]
            )["symbol"]

        report = (

            "📊 MARKET STATUS\n\n"

            f"Bullish : {len(bullish)}\n"
            f"Neutral : {len(neutral)}\n"
            f"Bearish : {len(bearish)}\n\n"

            f"Market Mood : {mood}\n\n"

            f"Top Bull : {top_bull}\n"
            f"Top Bear : {top_bear}"
        )

        return report

    except Exception as e:

        return (
            f"❌ MARKET ERROR\n{e}"
        )