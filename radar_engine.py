import json
import random

from logger_engine import log_info


# BIST örnek hisse listesi
symbols = [
    "TUPRS","KCHOL","EKGYO","ASELS","THYAO",
    "BIMAS","EREGL","SISE","PETKM","TCELL",
    "HALKB","DOAS","KRDMD","ALARK","ASTOR"
]


def generate_radar():

    radar = []

    for symbol in symbols:

        price = round(random.uniform(10, 500), 2)

        rsi = random.randint(10, 80)

        momentum = random.randint(-5, 10)

        score = 50

        score += momentum

        if rsi < 30:
            score += 20

        if rsi > 70:
            score -= 10

        radar.append([symbol, score, price, rsi])


    radar = sorted(radar, key=lambda x: x[1], reverse=True)

    radar = radar[:10]


    with open("radar.json", "w") as f:
        json.dump(radar, f)


    log_info("Ultra Radar Updated")


if __name__ == "__main__":
    generate_radar()
