from model_retrainer import retrain_model
from strategy_evolver import evolve_strategy


def self_learning_cycle(signals, strategy_params):

    retrain_model(signals)

    new_params = evolve_strategy(strategy_params)

    return new_params
