import json
import random
from logger_engine import log_info


def calculate_momentum():

    try:
        with open("radar.json","r") as f:
            radar = json.load(f)
    except:
        log_info("Radar data missing")
        return


    momentum_list = []


    for r in radar:

        try:

            symbol = r[0]
            score = r[1]
            price = r[2]
            rsi = r[3]

            volume_boost = random.uniform(0.9,1.2)
            trend_boost = random.uniform(0.9,1.3)

            momentum = round(score * volume_boost * trend_boost,2)

            momentum_list.append({

                "symbol": symbol,
                "score": score,
                "price": price,
                "rsi": rsi,
                "momentum": momentum

            })

        except:
            continue


    momentum_list = sorted(momentum_list, key=lambda x: x["momentum"], reverse=True)


    with open("momentum.json","w") as f:
        json.dump(momentum_list,f)


    log_info("Momentum Engine Completed")



if __name__ == "__main__":

    calculate_momentum()
