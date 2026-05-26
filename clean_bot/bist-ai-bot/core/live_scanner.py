from core.indicator_engine import analyze_stock
from core.telegram_notifier import send_ai_signal

# GLOBAL MEMORY
signal_memory = {}

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


def scan_market():

    opportunities = []

    print("\n========== NEW MARKET SCAN ==========\n")

    for symbol in symbols:

        try:

            result = analyze_stock(symbol)

            if not result:
                continue

            score = result["score"]
            signal = result["signal"]
            trend = result["trend"]

            print(
                f"{symbol} | Score:{score} | Signal:{signal} | Trend:{trend}"
            )

            # SIGNAL FILTER
            if signal is not None and score >= 20:

                signal_key = f"{symbol}_{signal}_{score}"

                # DUPLICATE BLOCKER
                if signal_key in signal_memory:

                    print(f"[FILTERED] Cooldown Active -> {signal_key}")
                    continue

                # SAVE MEMORY
                signal_memory[signal_key] = True

                opportunities.append(result)

                send_ai_signal(result)

        except Exception as e:

            print(f"[ERROR] {symbol} -> {e}")

    print("\n========== TOP OPPORTUNITIES ==========\n")

    sorted_opps = sorted(
        opportunities,
        key=lambda x: x["score"],
        reverse=True
    )

    for opp in sorted_opps:

        print(
            f"{opp['symbol']} | "
            f"Score:{opp['score']} | "
            f"Signal:{opp['signal']} | "
            f"Trend:{opp['trend']}"
        )

    return sorted_opps