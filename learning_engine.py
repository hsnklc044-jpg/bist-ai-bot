import json
from logger_engine import log_info


def run_learning():

    try:
        with open("trade_memory.json","r") as f:
            trades = json.load(f)
    except:
        log_info("Trade memory missing")
        return


    if len(trades) == 0:
        return


    wins = 0
    losses = 0
    total_profit = 0


    for t in trades:

        profit = t["profit"]

        total_profit += profit

        if profit > 0:
            wins += 1
        else:
            losses += 1


    win_rate = wins / len(trades)


    learning = {
        "total_trades": len(trades),
        "win_rate": round(win_rate,2),
        "total_profit": round(total_profit,2)
    }


    with open("learning.json","w") as f:
        json.dump(learning,f)


    log_info("Learning Engine Updated")


if __name__ == "__main__":
    run_learning()
