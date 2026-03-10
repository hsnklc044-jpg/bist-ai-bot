import random


def evolve_strategy(params):

    new_params = params.copy()

    if "rsi_threshold" in new_params:

        change = random.choice([-2, -1, 1, 2])

        new_params["rsi_threshold"] += change

    return new_params
