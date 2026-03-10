import json
import os

FILE = "ai_learning_data.json"


DEFAULT_WEIGHTS = {

    "trend": 1.0,
    "volume": 1.0,
    "institutional": 1.0,
    "relative_strength": 1.0
}


def load_weights():

    if not os.path.exists(FILE):

        return DEFAULT_WEIGHTS

    with open(FILE, "r") as f:

        return json.load(f)


def save_weights(weights):

    with open(FILE, "w") as f:

        json.dump(weights, f)


def update_weights(signal, result):

    weights = load_weights()

    factor_list = [

        "trend",
        "volume_spike",
        "institutional",
        "relative_strength"
    ]

    for f in factor_list:

        if signal.get(f):

            if result == "WIN":

                weights[f] += 0.02

            else:

                weights[f] -= 0.02

                if weights[f] < 0.2:
                    weights[f] = 0.2

    save_weights(weights)
