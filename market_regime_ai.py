import yfinance as yf
from regime_features import extract_regime_features
from regime_model import load_model


def detect_market_regime():

    try:

        data = yf.download("^XU100", period="1y", progress=False)

        features = extract_regime_features(data)

        model = load_model()

        prediction = model.predict([features])[0]

        regimes = {
            0: "SIDEWAYS",
            1: "BULL",
            2: "BEAR"
        }

        return regimes.get(prediction, "UNKNOWN")

    except:

        return "UNKNOWN"
