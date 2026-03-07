def allocate_capital(strategies, capital):

    allocation = {}

    n = len(strategies)

    if n == 0:
        return allocation

    per_strategy = capital / n

    for name in strategies:

        allocation[name] = per_strategy

    return allocation
