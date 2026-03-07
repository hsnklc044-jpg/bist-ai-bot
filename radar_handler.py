from scanner import scan_market


def run_radar_cycle():

    print("📡 Market taranıyor...")

    signals = scan_market()

    if signals:
        print("🚨 Sinyaller:")
        for s in signals:
            print(s["ticker"], s["signal"], s["entry"])
    else:
        print("Sinyal bulunamadı")

    return signals
