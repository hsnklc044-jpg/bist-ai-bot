from ml_model import load_model, save_model


def train_model(features, labels):

    model = load_model()

    model.fit(features, labels)

    save_model(model)

    return model
