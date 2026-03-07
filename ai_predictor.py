from ai_model_engine import load_model


def predict_signal(features):

    model = load_model()

    prediction = model.predict([features])[0]

    if prediction == 1:
        return "BUY"

    return "SKIP"
