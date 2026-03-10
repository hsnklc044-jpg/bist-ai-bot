STRATEGIES = {}


def register_strategy(name, strategy):

    STRATEGIES[name] = strategy


def get_strategies():

    return STRATEGIES
