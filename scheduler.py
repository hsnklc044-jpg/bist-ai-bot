from engine.market_hours import bist_market_open
from engine.ultimate_scanner import run_ultimate_scanner


def radar():

    if not bist_market_open():

        print("BIST kapalı")

        return

    print("📡 BIST radar çalışıyor...")

    run_ultimate_scanner()
