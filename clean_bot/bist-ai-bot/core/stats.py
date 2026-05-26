import json
import os

POSITIONS_FILE = "data/positions.json"
CLOSED_FILE = "data/closed_positions.json"


def load_json(path):
    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        return json.load(f)


def get_statistics():

    open_positions = load_json(POSITIONS_FILE)
    closed_positions = load_json(CLOSED_FILE)

    total_open = len(open_positions)

    total_closed = len(closed_positions)

    wins = 0
    losses = 0

    total_pnl = 0

    for symbol, trade in closed_positions.items():

        pnl = trade.get("pnl", 0)

        total_pnl += pnl

        if pnl > 0:
            wins += 1
        else:
            losses += 1

    win_rate = 0

    if total_closed > 0:
        win_rate = round((wins / total_closed) * 100, 2)

    return {
        "open_positions": total_open,
        "closed_positions": total_closed,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "total_pnl": round(total_pnl, 2)
    }