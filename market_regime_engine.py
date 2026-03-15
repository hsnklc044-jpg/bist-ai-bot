import json
import random
from logger_engine import log_info


def detect_market_regime():

    try:
        with open("momentum.json","r") as f:
            data = json.load(f)
    except:
        log_info("Momentum data missing")
        return


    avg_momentum = sum([x["momentum"] for x in data]) / len(data)


    if avg_momentum > 90:
        regime = "BULL"

    elif avg_momentum > 70:
        regime = "SIDEWAYS"

    else:
        regime = "BEAR"


    result = {
        "market_regime": regime,
        "avg_momentum": round(avg_momentum,2)
    }


    with open("market_regime.json","w") as f:
        json.dump(result,f)


    log_info(f"Market Regime: {regime}")


if __name__ == "__main__":

    detect_market_regime()
