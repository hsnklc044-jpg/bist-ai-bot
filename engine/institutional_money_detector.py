import pandas as pd


def detect_institutional_activity(df):

    try:

        avg_volume = df["Volume"].rolling(30).mean()

        current_volume = df["Volume"].iloc[-1]

        volume_ratio = current_volume / avg_volume.iloc[-1]

        price_change = (
            df["Close"].iloc[-1] - df["Close"].iloc[-2]
        ) / df["Close"].iloc[-2]

        # kurumsal alım kriteri
        if volume_ratio > 2 and price_change > 0:

            return {
                "institutional_activity": True,
                "volume_ratio": round(volume_ratio, 2)
            }

        return {
            "institutional_activity": False,
            "volume_ratio": round(volume_ratio, 2)
        }

    except Exception as e:

        print("Institutional detection error:", e)

        return {
            "institutional_activity": False,
            "volume_ratio": 0
        }
