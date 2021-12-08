import numpy as np
from scipy import stats
import stats_arrays as sa

# Local files
from .constants import compute_three_sigma_q

DISTRIBUTIONS_DICT = {choice.id: choice for choice in sa.uncertainty_choices}
Q_LOW, Q_HIGH, _ = compute_three_sigma_q()


def check_inputs(parameters, sample, distribution):
    """Check that inputs that are passed to functions are in the right format."""
    # Make sure all parameters have proper distributions
    assert np.all(parameters["uncertainty_type"] == distribution.id)
    # Make sure len of parameters is equal to len of sample
    assert parameters.shape[0] == sample.shape[0]


def convert_sample_to_normal_or_lognormal(parameters, sample, distribution):
    """Convert uniform in [0,1] to NORMAL or LOGNORMAL distribution."""

    min_val = distribution.cdf(parameters, parameters["minimum"]).squeeze()
    mask_is_nan_min = np.asarray(np.isnan(min_val).squeeze()).nonzero()[0]
    np.put(min_val, mask_is_nan_min, Q_LOW)

    max_val = distribution.cdf(parameters, parameters["maximum"]).squeeze()
    mask_is_nan_max = np.asarray(np.isnan(max_val).squeeze()).nonzero()[0]
    np.put(max_val, mask_is_nan_max, Q_HIGH)

    q = (max_val - min_val) * sample + min_val
    params_converted = distribution.ppf(parameters, q).squeeze()

    # which values of params_converted are equal to +-inf? -> replace with Q_HIGH and Q_LOW
    mask_is_neg_inf = np.where(params_converted == -np.inf)[0]
    mask_is_pos_inf = np.where(params_converted == np.inf)[0]

    q_low_ppf = distribution.ppf(
        parameters[mask_is_neg_inf], np.array([Q_LOW] * mask_is_neg_inf.shape[0])
    )
    q_high_ppf = distribution.ppf(
        parameters[mask_is_pos_inf], np.array([Q_HIGH] * mask_is_pos_inf.shape[0])
    )

    np.put(params_converted, mask_is_neg_inf, q_low_ppf)
    np.put(params_converted, mask_is_pos_inf, q_high_ppf)

    return params_converted


def convert_sample_to_truncated_triang(parameters, sample):
    """
    Convert uniform in [0,1] to TRUNCATED TRIANGULAR distribution
    TODO check correctness and update in stats_arrays
    """

    q_low_t = stats.triang.cdf(
        parameters["minimum"],
        c=parameters["shape"],
        loc=parameters["loc"],
        scale=parameters["scale"],
    )
    q_high_t = stats.triang.cdf(
        parameters["maximum"],
        c=parameters["shape"],
        loc=parameters["loc"],
        scale=parameters["scale"],
    )
    q_t = (q_high_t - q_low_t) * sample + q_low_t
    params_converted = stats.triang.ppf(
        q_t, c=parameters["shape"], loc=parameters["loc"], scale=parameters["scale"]
    )
    return params_converted


def convert_sample(parameters, sample):
    """Convert all samples to correct distributions."""

    # Identify distribution
    distr = DISTRIBUTIONS_DICT[parameters["uncertainty_type"][0]]
    # Check that all params have this distribution
    check_inputs(parameters, sample, distr)
    if distr == sa.NormalUncertainty or distr == sa.LognormalUncertainty:
        return convert_sample_to_normal_or_lognormal(parameters, sample, distr)
    elif distr == sa.TriangularUncertainty:
        converted = np.empty(len(sample))
        loc_nan = np.where(np.isnan(parameters["scale"]))[0]
        loc_not_nan = np.setdiff1d(np.arange(len(sample)), loc_nan)
        converted[loc_nan] = distr.ppf(parameters[loc_nan], sample[loc_nan]).flatten()
        converted[loc_not_nan] = convert_sample_to_truncated_triang(
            parameters[loc_not_nan], sample[loc_not_nan]
        ).flatten()
        return converted
    else:
        return distr.ppf(parameters, sample)
