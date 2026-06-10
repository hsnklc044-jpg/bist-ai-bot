import json
import os

from core.indicator_engine import analyze_stock
from core.telegram_notifier import send_ai_signal
from core.logger import write_log

MEMORY_FILE = "data/signal_memory.json"


def load_memory():

    if not os.path.exists(
        MEMORY_FILE
    ):
        return {}

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return {}


def save_memory(memory):

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            memory,
            f,
            indent=4
        )


signal_memory = load_memory()

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

    global signal_memory

    opportunities = []

    print(
        "\n========== NEW MARKET SCAN ==========\n"
    )

    for symbol in symbols:

        try:

            result = analyze_stock(
                symbol
            )

            if not result:
                continue

            score = result["score"]
            signal = result["signal"]
            trend = result["trend"]

            print(
                f"{symbol} | "
                f"Score:{score} | "
                f"Signal:{signal} | "
                f"Trend:{trend}"
            )

            if signal not in [
                "BUY",
                "STRONG BUY",
                "SELL",
                "STRONG SELL"
            ]:
                continue

            if score < 60:
                continue

            signal_key = (
                f"{symbol}_{signal}_{int(score)}"
            )

            if signal_key in signal_memory:

                print(
                    f"[FILTERED] "
                    f"{signal_key}"
                )

                continue

            signal_memory[
                signal_key
            ] = True

            save_memory(
                signal_memory
            )

            opportunities.append(
                result
            )

            send_ai_signal(
                result
            )

            write_log(
                f"SIGNAL SENT | "
                f"{symbol} | "
                f"{signal}"
            )

        except Exception as e:

            write_log(
                f"SCAN ERROR | "
                f"{symbol} | "
                f"{e}"
            )

    sorted_opps = sorted(
        opportunities,
        key=lambda x: x["score"],
        reverse=True
    )

    print(
        "\n========== TOP OPPORTUNITIES ==========\n"
    )

    for opp in sorted_opps:

        print(
            f"{opp['symbol']} | "
            f"Score:{opp['score']} | "
            f"Signal:{opp['signal']} | "
            f"Trend:{opp['trend']}"
        )

    write_log(
        f"MARKET SCAN COMPLETE | "
        f"SIGNALS={len(sorted_opps)}"
    )

    return sorted_opps