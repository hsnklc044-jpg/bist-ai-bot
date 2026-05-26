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


def get_top_signal():

    try:

        longs = []

        for symbol in SYMBOLS:

            result = ai_filter_stock(symbol)

            if not result:
                continue

            if result["signal"] not in [
                "BUY",
                "STRONG BUY"
            ]:
                continue

            longs.append(result)

        if not longs:

            return "❌ BUY sinyali yok"

        best_signal = max(
            longs,
            key=lambda x: (
                x["score"] * 3
                + x["confidence"]
                + x["bull_score"]
                + (x["volume_ratio"] * 10)
            )
        )

        report = (

            "🔥 TOP SIGNAL\n\n"

            f"{best_signal['symbol']}\n\n"

            f"AI Score : "
            f"{best_signal['score']}\n"

            f"Trend : "
            f"{best_signal['trend']}\n"

            f"Confidence : "
            f"{best_signal['confidence']}%\n\n"

            f"ATR : "
            f"{best_signal['atr']}\n\n"

            f"Entry : "
            f"{best_signal['entry_price']}\n"

            f"Stop : "
            f"{best_signal['stop_loss']}\n"

            f"Target 1 : "
            f"{best_signal['target_1']}\n"

            f"Target 2 : "
            f"{best_signal['target_2']}"
        )

        return report

    except Exception as e:

        return (
            f"❌ TOP SIGNAL ERROR\n{e}"
        )