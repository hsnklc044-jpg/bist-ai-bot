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


def generate_watchlist():

    try:

        candidates = []

        for symbol in SYMBOLS:

            result = ai_filter_stock(symbol)

            if not result:
                continue

            if result["signal"] in [
                "BUY",
                "STRONG BUY"
            ]:

                candidates.append(result)

        candidates = sorted(
            candidates,
            key=lambda x: (
                x["score"],
                x["confidence"]
            ),
            reverse=True
        )

        report = "🟢 WATCHLIST\n\n"

        if not candidates:

            report += "Uygun hisse bulunamadı."

            return report

        for item in candidates:

            report += (

                f"{item['symbol']}\n"
                f"Score : {item['score']}\n"
                f"Confidence : {item['confidence']}%\n\n"
            )

        return report

    except Exception as e:

        return f"❌ WATCHLIST ERROR\n{e}"