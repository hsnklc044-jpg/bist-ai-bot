import pandas as pd


def clean_data(data):

    if data is None:
        return None

    data = data.dropna()

    if len(data) == 0:
        return None

    return data
