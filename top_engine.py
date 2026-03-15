from radar_engine import run_radar


def get_top():

    radar = run_radar()

    if not radar:
        return []

    # en yüksek skorları al
    top = sorted(radar, key=lambda x: x[1], reverse=True)

    return top[:5]
