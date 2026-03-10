import numpy as np


def covariance_matrix(returns):

    return np.cov(returns.T)
