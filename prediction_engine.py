import json
import random

from logger_engine import log_info


def generate_predictions():

    try:

        with open("radar.json","r") as f:
            radar = json.load(f)

    except:
        radar = []


    predictions = []

    for r in radar:

        symbol = r[0]
        score = r[1]

        confidence = round(random.uniform(0.45,0.75),2)

        direction = "UP"

        if score < 60:
            direction = "NEUTRAL"

        if score < 50:
            direction = "DOWN"


        predictions.append({
            "symbol":symbol,
            "prediction":direction,
            "confidence":confidence
        })


    with open("predictions.json","w") as f:
        json.dump(predictions,f)


    log_info("AI Predictions Updated")


if __name__ == "__main__":
    generate_predictions()
