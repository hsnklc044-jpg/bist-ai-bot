from fastapi import FastAPI
from app.data_utils import get_data
from app.strategy import generate_signal
from app.backtest import run_backtest
from app.telegram_utils import send_telegram

app = FastAPI()


@app.get("/")
def root():
    return {"status": "16.4 STABLE CORE AKTİF"}


@app.get("/backtest")
def backtest():

    df = get_data()

    result = run_backtest(df)

    return result


@app.get("/morning_report")
def morning_report():

    df = get_data()

    signal = generate_signal(df)

    if signal is None:
        return {"message": "Henüz sinyal yok"}

    message = (
        f"🚀 SABAH SİNYALİ\n"
        f"Yön: {signal['side']}\n"
        f"Fiyat: {signal['price']}\n"
        f"RSI: {round(signal['rsi'],2)}"
    )

    send_telegram(message)

    return {"status": "Morning Signals Sent"}
