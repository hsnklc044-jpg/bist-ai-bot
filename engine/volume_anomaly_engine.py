def detect_volume_anomaly(df):

    try:

        volume = df["Volume"]

        avg_volume = volume.rolling(20).mean()

        anomaly = volume.iloc[-1] > avg_volume.iloc[-1] * 2

        return {
            "volume_anomaly": anomaly
        }

    except Exception as e:

        print("Volume anomaly error:", e)

        return {
            "volume_anomaly": False
        }
