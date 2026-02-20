from fastapi import FastAPI
from app.data_engine import DataEngine
from app.scoring_engine import ScoringEngine

app = FastAPI()

data_engine = DataEngine()
scoring_engine = ScoringEngine()


@app.get("/")
def root():
    return {"status": "BIST Institutional Engine aktif"}


@app.get("/analyze/{symbol}")
def analyze_stock(symbol: str):

    df = data_engine.get_price_data(symbol)

    result = scoring_engine.calculate_score(df)

    return {
        "symbol": symbol.upper(),
        "score": result["score"],
        "signal": result["signal"]
    }
