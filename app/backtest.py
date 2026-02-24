import pandas as pd
from app.strategy import generate_signal


def run_backtest(df):

    try:
        if df is None or df.empty:
            return {"error": "Data boş"}

        if "close" not in df.columns:
            return {"error": "close kolonu yok"}

        trades = []
        position = None

        for i in range(50, len(df)):

            sub_df = df.iloc[:i]

            signal = generate_signal(sub_df)

            if signal is None:
                continue

            price = float(sub_df["close"].iloc[-1])

            # LONG giriş
            if signal["side"] == "BUY" and position is None:
                position = price

            # LONG çıkış
            elif signal["side"] == "SELL" and position is not None:
                pnl = price - position
                trades.append(pnl)
                position = None

        total_pnl = round(sum(trades), 2)
        win_rate = round(
            (len([t for t in trades if t > 0]) / len(trades) * 100)
            if trades else 0,
            2
        )

        return {
            "Toplam PnL": total_pnl,
            "Win Rate %": win_rate,
            "Trade Sayısı": len(trades)
        }

    except Exception as e:
        return {"error": str(e)}
