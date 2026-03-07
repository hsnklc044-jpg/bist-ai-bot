import pickle
import os
from sklearn.ensemble import RandomForestClassifier

MODEL_FILE = "ai_trading_model.pkl"


def load_model():

    if os.path.exists(MODEL_FILE):

        with open(MODEL_FILE, "rb") as f:
            return pickle.load(f)

    return RandomForestClassifier(n_estimators=200)


def save_model(model):

    with open(MODEL_FILE, "wb") as f:
        pickle.dump(model, f)
