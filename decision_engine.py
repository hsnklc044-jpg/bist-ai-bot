import json
from logger_engine import log_info


def run_decision_engine():

    try:
        with open("predictions.json","r") as f:
            data = json.load(f)
    except:
        log_info("Prediction file missing")
        return

    decisions = []

    for r in data:

        score = r.get("score",0)
        confidence = r.get("confidence",0)

        if score >= 75 and confidence >= 0.6:
            decision = "BUY"

        elif score >= 60:
            decision = "WATCH"

        else:
            decision = "AVOID"

        r["decision"] = decision

        decisions.append(r)

    with open("decisions.json","w") as f:
        json.dump(decisions,f)

    log_info("Decision Engine Completed")


if __name__ == "__main__":

    run_decision_engine()
