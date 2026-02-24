import yfinance as yf
from ai_signal_engine import calculate_rsi, calculate_ema

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
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)

            if df.empty:
                continue

            close = df["Close"]

            rsi = calculate_rsi(close)
            ema50 = calculate_ema(close, 50)

            if rsi is None or ema50 is None:
                continue

            current_price = close.iloc[-1]

            # 🔵 YUKARI TREND + RSI DÜŞÜK → ALIM
            if current_price > ema50 and rsi < 35:
                signals.append(
                    f"🟢 AL Sinyali\n"
                    f"{symbol}\n"
                    f"Fiyat: {round(current_price,2)}\n"
                    f"RSI: {round(rsi,2)}\n"
                    f"Trend: Yukarı (EMA50 üstü)"
                )

            # 🔴 AŞAĞI TREND + RSI YÜKSEK → SATIM
            elif current_price < ema50 and rsi > 65:
                signals.append(
                    f"🔴 SAT Sinyali\n"
                    f"{symbol}\n"
                    f"Fiyat: {round(current_price,2)}\n"
                    f"RSI: {round(rsi,2)}\n"
                    f"Trend: Aşağı (EMA50 altı)"
                )

        except Exception as e:
            print(f"Hata {symbol}: {e}")
            continue

    return signals
