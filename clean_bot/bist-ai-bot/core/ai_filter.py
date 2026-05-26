from core.indicator_engine import analyze_stock


def ai_filter_stock(symbol):

    try:

        if not isinstance(symbol, str):
            return None

        data = analyze_stock(symbol)

        if data is None:
            return None

        return {
            "symbol": data.get("symbol"),
            "price": data.get("price", 0),

            "score": data.get("score", 0),
            "trend": data.get("trend", "SIDEWAYS"),
            "signal": data.get("signal", "WATCH"),

            "confidence": data.get("confidence", 0),

            "rsi": data.get("rsi", 50),
            "macd": data.get("macd", 0),

            "volatility": data.get("volatility", 0),
            "volume_ratio": data.get("volume_ratio", 1),

            "bull_score": data.get("bull_score", 0),
            "bear_score": data.get("bear_score", 0),

            "atr": data.get("atr", 0),

            "entry_price": data.get("entry_price", 0),
            "stop_loss": data.get("stop_loss", 0),
            "target_1": data.get("target_1", 0),
            "target_2": data.get("target_2", 0)
        }

    except Exception as e:

        print(
            f"[AI FILTER ERROR] "
            f"{symbol}: {e}"
        )

        return None