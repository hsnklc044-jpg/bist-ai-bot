import pickle
import os
from sklearn.tree import DecisionTreeClassifier

MODEL_FILE = "regime_model.pkl"


def load_model():

    if os.path.exists(MODEL_FILE):

        with open(MODEL_FILE, "rb") as f:
            return pickle.load(f)

    return DecisionTreeClassifier()


def save_model(model):

    with open(MODEL_FILE, "wb") as f:
        pickle.dump(model, f)
