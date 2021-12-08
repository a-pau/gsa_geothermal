from math import exp, pi
from scipy.integrate import quad
import numpy as np


def compute_three_sigma_q():
    """
    Calculate area under normal distribution within +-3 sigma interval from the mean.
    Probability of a value to fall within this interval is THREE_SIGMA_Q = 99.7%.
    This way tails of normal/lognormal distribution can be neglected.
    """
    mu, sigma = 0, 1  # mean and standard deviation
    THREE_SIGMA_Q = quad(
        lambda x: 1
        / np.sqrt(2 * pi * sigma ** 2)
        * exp(-((x - mu) ** 2) / (2 * sigma ** 2)),
        -3 * sigma,
        +3 * sigma,
    )[0]
    Q_LOW = (1 - THREE_SIGMA_Q) / 2
    Q_HIGH = (1 + THREE_SIGMA_Q) / 2
    return Q_LOW, Q_HIGH, THREE_SIGMA_Q
