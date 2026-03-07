def calculate_pnl(trades):

    total_return = sum(trades)

    if len(trades) == 0:
        avg_return = 0
    else:
        avg_return = total_return / len(trades)

    return {
        "total_return": round(total_return,2),
        "avg_return": round(avg_return,2),
        "trades": len(trades)
    }
