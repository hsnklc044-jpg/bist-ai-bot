from fastapi import FastAPI
from app.data_utils import get_data
from app.strategy import generate_signal
from app.backtest import run_backtest
from app.telegram_utils import send_telegram
from app.scanner import scan_market

app = FastAPI()


# ================= ROOT =================

@app.get("/")
def root():
    return {"status": "16.8 PRO SCAN BUILD AKTİF"}


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
            return {"error": "close kolonu yok"}

        result = run_backtest(df)

        return result

    except Exception as e:
        return {"error": str(e)}


# ================= MORNING SIGNAL =================

@app.get("/morning_report")
def morning_report():
    try:
        df = get_data()

        if df is None or df.empty:
            return {"error": "Veri yok"}

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

        return {"status": "Morning Signal Sent"}

    except Exception as e:
        return {"error": str(e)}


# ================= BIST30 SABAH TARAMA =================

@app.get("/morning_scan")
def morning_scan():

    try:
        top3 = scan_market()

        if not top3:
            return {"message": "Veri bulunamadı"}

        message = "🚀 BIST30 SABAH TARAMA\n\n"

        for i, stock in enumerate(top3, 1):
            message += f"{i}️⃣ {stock['symbol']} | RSI: {stock['rsi']} | Skor: {stock['score']}\n"

        send_telegram(message)

        return {"status": "Sabah Tarama Gönderildi"}

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
