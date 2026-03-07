from ai_dataset_builder import build_dataset
from ai_model_engine import load_model, save_model


def retrain_model(signals):

    X, y = build_dataset(signals)

    if len(X) < 10:
        return None

    model = load_model()

    model.fit(X, y)

    save_model(model)

    return "Model retrained"
