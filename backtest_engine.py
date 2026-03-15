import json
import random

from logger_engine import log_info


def run_backtest():

    trades = 200
    wins = 0
    total_profit = 0

    for i in range(trades):

        profit = random.uniform(-0.03,0.05)

        total_profit += profit

        if profit > 0:
            wins += 1


    win_rate = round((wins / trades) * 100,2)
    avg_profit = round((total_profit / trades) * 100,2)

    result = {
        "trades": trades,
        "win_rate": win_rate,
        "avg_profit": avg_profit
    }

    with open("backtest.json","w") as f:
        json.dump(result,f)

    log_info("Backtest Completed")


if __name__ == "__main__":
    run_backtest()
