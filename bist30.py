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

            entry = close.iloc[-1]
            ema50_now = ema50.iloc[-1]
            ema200_now = ema200.iloc[-1]
            rsi_now = rsi_series.iloc[-1]
            rsi_prev = rsi_series.iloc[-2]
            atr_now = atr_series.iloc[-1]

            trend_ok = entry > ema50_now and ema50_now > ema200_now
            rsi_cross = rsi_prev < 30 and rsi_now > 30
            volume_ok = (
                volume.iloc[-1] > volume.iloc[-2] and
                volume.iloc[-2] > volume.iloc[-3]
            )

            stop = ema50_now
            target = entry + (2.5 * atr_now)

            risk = entry - stop
            reward = target - entry

            if risk <= 0:
                continue

            rr_ratio = reward / risk

            if (
                trend_ok and
                rsi_cross and
                volume_ok and
                rr_ratio >= 1.8 and
                is_new_signal(symbol)
            ):

                # Skor Hesaplama
                score = (
                    rr_ratio * 40 +
                    (50 - abs(50 - rsi_now)) * 0.6 +
                    (volume.iloc[-1] / volume.iloc[-2]) * 10
                )

                message = (
                    f"🚀 ELİT AL Sinyali\n\n"
                    f"{symbol}\n"
                    f"Giriş: {round(entry,2)}\n"
                    f"Stop: {round(stop,2)}\n"
                    f"Hedef: {round(target,2)}\n"
                    f"R/R: {round(rr_ratio,2)}\n"
                    f"RSI: {round(rsi_now,2)}\n"
                    f"Skor: {round(score,2)}"
                )

                signals.append((score, message))
                store_signal(symbol)

        except Exception as e:
            print(f"Hata {symbol}: {e}")
            continue

    # Skora göre sırala
    signals = sorted(signals, key=lambda x: x[0], reverse=True)

    # Sadece en iyi 3
    return [s[1] for s in signals[:3]]
