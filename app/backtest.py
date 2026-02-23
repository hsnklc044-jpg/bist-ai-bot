from strategy import generate_signal


def run_backtest(data):

    if data is None or data.empty:
        return {"message": "Veri yok"}

    signal = generate_signal(data)

    if signal is None:
        return {"message": "Henüz sinyal yok"}

    return {
        "side": signal["side"],
        "price": float(signal["price"]),
        "rsi": float(signal["rsi"])
    }
