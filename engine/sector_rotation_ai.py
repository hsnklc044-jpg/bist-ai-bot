import yfinance as yf

SECTOR_MAP = {

    "BANK": ["AKBNK", "GARAN", "YKBNK", "ISCTR"],

    "HOLDING": ["KCHOL", "SAHOL"],

    "ENERGY": ["ENJSA", "AKSEN"],

    "DEFENSE": ["ASELS"],

    "TECH": ["MIATK"]
}


def sector_strength():

    scores = {}

    for sector, stocks in SECTOR_MAP.items():

        perf = []

        for s in stocks:

            try:

                df = yf.download(
                    f"{s}.IS",
                    period="1mo",
                    interval="1d",
                    progress=False
                )

                change = (df["Close"].iloc[-1] - df["Close"].iloc[0]) / df["Close"].iloc[0]

                perf.append(change)

            except:

                pass

        if len(perf) > 0:

            scores[sector] = sum(perf) / len(perf)

    if not scores:
        return None

    strongest = max(scores, key=scores.get)

    return strongest
