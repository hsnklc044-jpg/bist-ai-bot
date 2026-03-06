from engine.ultimate_scanner import ultimate_scanner


def get_heatmap():

    signals = ultimate_scanner()

    if not signals:
        return None

    return signals
