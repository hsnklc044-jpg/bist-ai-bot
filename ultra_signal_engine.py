import json
from logger_engine import log_info


def run_ultra_signals():

    try:
        with open("risk.json","r") as f:
            data = json.load(f)
    except:
        log_info("Risk data missing")
        return


    # score'a göre sırala
    data = sorted(data, key=lambda x: x["score"], reverse=True)


    # sadece en iyi 3
    top = data[:3]


    with open("ultra_signals.json","w") as f:
        json.dump(top,f)


    log_info("Ultra signals generated")


if __name__ == "__main__":
    run_ultra_signals()
