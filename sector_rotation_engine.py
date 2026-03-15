import json
from sector_engine import get_sector

TRADE_FILE = "trades.json"


def detect_strong_sectors():

    try:
        with open(TRADE_FILE,"r") as f:
            trades = json.load(f)
    except:
        return {}

    sector_count = {}

    for trade in trades:

        sector = get_sector(trade["symbol"])

        if sector not in sector_count:
            sector_count[sector] = 0

        sector_count[sector] += 1

    return sector_count
