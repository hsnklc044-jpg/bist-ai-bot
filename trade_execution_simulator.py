import random


def simulate_execution(signal):

    success = random.choice([True, False])

    if success:

        return {
            "ticker": signal["ticker"],
            "result": "WIN"
        }

    return {
        "ticker": signal["ticker"],
        "result": "LOSS"
    }
