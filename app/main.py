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

    # 1️⃣ Veri çek
    df = data_engine.get_price_data(symbol)

    if df is None or df.empty:
        return {
            "symbol": symbol,
            "score": 0,
            "signal": "VERİ YETERSİZ"
        }

    # 2️⃣ İndikatör hesapla
    df = data_engine.calculate_indicators(df)

    if df is None or df.empty:
        return {
            "symbol": symbol,
            "score": 0,
            "signal": "VERİ YETERSİZ"
        }

    # 3️⃣ Skor hesapla
    score, signal = scoring_engine.calculate_score(df)

    # 4️⃣ JSON döndür
    return {
        "symbol": symbol,
        "score": score,
        "signal": signal
    }
