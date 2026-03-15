import json

from logger_engine import log_info


def generate_portfolio():

    try:
        with open("radar.json","r") as f:
            radar = json.load(f)
    except:
        radar = []


    portfolio = []

    total_score = sum([r[1] for r in radar])


    for r in radar:

        symbol = r[0]
        score = r[1]
        price = r[2]

        weight = round((score / total_score) * 100,2)

        portfolio.append({
            "symbol":symbol,
            "weight":weight,
            "price":price
        })


    with open("portfolio.json","w") as f:
        json.dump(portfolio,f)


    log_info("AI Portfolio Updated")


if __name__ == "__main__":
    generate_portfolio()
