from core.indicator_engine import analyze_stock

symbols = [
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


def get_top_signals():

    opportunities = []

    for symbol in symbols:

        try:

            result = analyze_stock(
                symbol
            )

            if not result:
                continue

            if result["signal"] not in [
                "BUY",
                "STRONG BUY",
                "SELL",
                "STRONG SELL"
            ]:
                continue

            if result["score"] < 60:
                continue

            opportunities.append(
                result
            )

        except Exception:
            continue

    opportunities = sorted(
        opportunities,
        key=lambda x: x["score"],
        reverse=True
    )

    return opportunities[:10]