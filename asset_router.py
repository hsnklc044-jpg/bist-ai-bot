def route_strategy(asset):

    if asset["market"] == "CRYPTO":
        return "MOMENTUM"

    if asset["market"] == "US":
        return "TREND"

    if asset["market"] == "BIST":
        return "QUANT"

    return "DEFAULT"
