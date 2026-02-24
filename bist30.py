import yfinance as yf
from ai_signal_engine import calculate_rsi, calculate_ema
from signal_memory import is_new_signal, store_signal

BIST30 = [
    "AKBNK.IS", "ASELS.IS", "BIMAS.IS", "EREGL.IS",
    "FROTO.IS", "GARAN.IS", "KCHOL.IS", "KOZAL.IS",
    "PETKM.IS", "SAHOL.IS", "SASA.IS", "SISE.IS",
    "TCELL.IS", "THYAO.IS", "TUPRS.IS"
]


def scan_bist30():
    signals = []

    for symbol in BIST30:
        try:
            df = yf.download(symbol, period="8mo", interval="1d", progress=False)

            if df.empty or len(df) < 210:
                continue

            close = df["Close"]
            volume = df["Volume"]

            rsi_series = calculate_rsi(close)
            ema50 = calculate_ema(close, 50)
            ema200 = calculate_ema(close, 200)

            current_price = close.iloc[-1]

            trend_up = (
                current_price > ema50.iloc[-1] and
                ema50.iloc[-1] > ema200.iloc[-1]
            )

            rsi_cross = (
                rsi_series.iloc[-2] < 30 and
                rsi_series.iloc[-1] > 30
            )

            volume_increase = (
                volume.iloc[-1] > volume.iloc[-2] and
                volume.iloc[-2] > volume.iloc[-3]
            )

            if trend_up and rsi_cross and volume_increase:

                if is_new_signal(symbol):

                    message = (
                        f"🚀 GÜÇLÜ AL Sinyali\n"
                        f"{symbol}\n"
                        f"Fiyat: {round(current_price,2)}\n"
                        f"RSI: {round(rsi_series.iloc[-1],2)}\n"
                        f"Trend: EMA50 > EMA200\n"
                        f"Hacim: Artıyor"
                    )

                    signals.append(message)
                    store_signal(symbol)

        except Exception as e:
            print(f"Hata {symbol}: {e}")
            continue

    return signals
