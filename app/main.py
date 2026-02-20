from fastapi import FastAPI
from app.data_engine import DataEngine
from app.scoring_engine import ScoringEngine
import os
import uvicorn

app = FastAPI()

data_engine = DataEngine()
scoring_engine = ScoringEngine()


@app.get("/")
def root():
    return {"status": "BIST Institutional Engine aktif"}


@app.get("/analyze/{symbol}")
def analyze_stock(symbol: str):

    df = data_engine.get_price_data(symbol)

    if df.empty:
        return {"error": "Veri alınamadı"}

    df = data_engine.calculate_indicators(df)

    result = scoring_engine.calculate_score(df)

    return {
        "symbol": symbol.upper(),
        "score": result["score"],
        "signal": result["signal"]
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
