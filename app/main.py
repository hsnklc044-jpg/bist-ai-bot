from fastapi import FastAPI
from app.data_utils import get_data
from app.strategy import generate_signal
from app.backtest import run_backtest
from app.telegram_utils import send_telegram

app = FastAPI()


# ================= ROOT =================

@app.get("/")
def root():
    return {"status": "16.7 STABLE DEBUG BUILD AKTİF"}


# ================= DATA TEST =================

@app.get("/data_test")
def data_test():
    try:
        df = get_data()

        if df is None:
            return {"error": "Veri None geldi"}

        if df.empty:
            return {"error": "Veri boş"}

        return {
            "rows": len(df),
            "columns": df.columns.tolist()
        }

    except Exception as e:
        return {"error": str(e)}


# ================= BACKTEST =================

@app.get("/backtest")
def backtest():
    try:
        df = get_data()

        if df is None:
            return {"error": "Veri None geldi"}

        if df.empty:
            return {"error": "Veri boş"}

        if "close" not in df.columns:
            return {
                "error": "close kolonu yok",
                "columns": df.columns.tolist()
            }

        result = run_backtest(df)

        return result

    except Exception as e:
        return {"error": str(e)}


# ================= MORNING REPORT =================

@app.get("/morning_report")
def morning_report():
    try:
        df = get_data()

        if df is None or df.empty:
            return {"error": "Veri yok"}

        if "close" not in df.columns:
            return {
                "error": "close kolonu yok",
                "columns": df.columns.tolist()
            }

        signal = generate_signal(df)

        if signal is None:
            return {"message": "Henüz sinyal yok"}

        message = (
            f"🚀 SABAH SİNYALİ\n"
            f"Yön: {signal['side']}\n"
            f"Fiyat: {round(float(signal['price']),2)}\n"
            f"RSI: {round(float(signal['rsi']),2)}"
        )

        send_telegram(message)

        return {"status": "Morning Signals Sent"}

    except Exception as e:
        return {"error": str(e)}


# ================= TELEGRAM TEST =================

@app.get("/telegram_test")
def telegram_test():
    try:
        send_telegram("TEST MESAJI 🚀")
        return {"status": "Gönderildi"}
    except Exception as e:
        return {"error": str(e)}
