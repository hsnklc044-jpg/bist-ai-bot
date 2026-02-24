import yfinance as yf
from ai_signal_engine import calculate_rsi, calculate_ema, calculate_atr
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
            atr_series = calculate_atr(df)

            current_price = close.iloc[-1]
            current_rsi = rsi_series.iloc[-1]
            current_ema50 = ema50.iloc[-1]
            current_ema200 = ema200.iloc[-1]
            current_atr = atr_series.iloc[-1]

            trend_up = (
                current_price > current_ema50 and
                current_ema50 > current_ema200
            )

            rsi_cross = (
                rsi_series.iloc[-2] < 30 and
                current_rsi > 30
            )

            volume_increase = (
                volume.iloc[-1] > volume.iloc[-2] and
                volume.iloc[-2] > volume.iloc[-3]
            )

            if trend_up and rsi_cross and volume_increase:

                if is_new_signal(symbol):

                    entry = current_price
                    stop = current_ema50
                    target = entry + (2 * current_atr)

                    risk = entry - stop
                    reward = target - entry

                    if risk <= 0:
                        continue

                    rr_ratio = round(reward / risk, 2)

                    message = (
                        f"🚀 GÜÇLÜ AL Sinyali\n\n"
                        f"{symbol}\n"
                        f"Giriş: {round(entry,2)}\n"
                        f"Stop: {round(stop,2)}\n"
                        f"Hedef: {round(target,2)}\n"
                        f"R/R: {rr_ratio}\n"
                        f"RSI: {round(current_rsi,2)}\n"
                        f"Trend: EMA50 > EMA200"
                    )

                    signals.append(message)
                    store_signal(symbol)

        except Exception as e:
            print(f"Hata {symbol}: {e}")
            continue

    return signals
