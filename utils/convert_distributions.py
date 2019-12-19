#TODO WOuld it make sense to split lognor such that it fits to cache??

from itertools import compress
import stats_arrays as sa
from scipy import stats
import numpy as np

# Local files
from .constants import *

DISTRIBUTIONS_DICT = {choice.id: choice for choice in sa.uncertainty_choices}


def check_inputs(params, sample, distr):
    """
    Check that inputs that are passed to functions are in the right format 
    """

    #Make sure all parameters have proper distributions
    assert np.all(params['uncertainty_type'] == distr.id)
    
    #Make sure len of parameters is equal to len of sample
    assert params.shape[0]==sample.shape[0]



def convert_sample_to_normal_or_lognormal(params, sample, distr):
    """
    Convert uniform in [0,1] to NORMAL or LOGNORMAL distribution
    """
    
    min_val = distr.cdf(params, params['minimum']).squeeze()
    mask_is_nan_min = np.asarray(np.isnan(min_val).squeeze()).nonzero()[0]
    np.put(min_val, mask_is_nan_min, Q_LOW)

    max_val = distr.cdf(params, params['maximum']).squeeze()
    mask_is_nan_max = np.asarray(np.isnan(max_val).squeeze()).nonzero()[0]
    np.put(max_val, mask_is_nan_max, Q_HIGH)
            
    q = (max_val - min_val)*sample + min_val
    params_converted = distr.ppf(params, q).squeeze()
        
    #which values of params_converted are equal to +-inf? -> replace with Q_HIGH and Q_LOW
    mask_is_neg_inf = np.where(params_converted == -np.inf)[0]
    mask_is_pos_inf = np.where(params_converted ==  np.inf)[0]
        
    q_low_ppf  = distr.ppf( params[mask_is_neg_inf], np.array([Q_LOW] *mask_is_neg_inf.shape[0]) )
    q_high_ppf = distr.ppf( params[mask_is_pos_inf], np.array([Q_HIGH]*mask_is_pos_inf.shape[0]) )
    
    np.put(params_converted, mask_is_neg_inf, q_low_ppf )
    np.put(params_converted, mask_is_pos_inf, q_high_ppf)
    
    return params_converted



def convert_sample_to_truncated_triang(params, sample):
    """
    Convert uniform in [0,1] to TRUNCATED TRIANGULAR distribution 
    TODO check correctness and update in stats_arrays
    """
    q_low_t  = stats.triang.cdf(params["minimum"], c=params["shape"], loc=params["loc"], scale=params["scale"])
    q_high_t = stats.triang.cdf(params["maximum"], c=params["shape"], loc=params["loc"], scale=params["scale"])
    q_t = (q_high_t - q_low_t)*sample + q_low_t
    params_converted = stats.triang.ppf(q_t, c=params["shape"], loc=params["loc"], scale=params["scale"])
    
    return params_converted



def convert_sample(params, sample):

    # Identify distribution
    distr = DISTRIBUTIONS_DICT[ params['uncertainty_type'][0] ]

    # Check that all params have this distribution
    check_inputs(params, sample, distr)

    if distr == sa.NormalUncertainty or distr == sa.LognormalUncertainty:
        return convert_sample_to_normal_or_lognormal(params, sample, distr)
    elif distr == sa.TriangularUncertainty:
        converted = np.empty(len(sample))
        loc_nan     = np.where(np.isnan(params["scale"]))[0]
        loc_not_nan = np.setdiff1d(np.arange(len(sample)), loc_nan)
        converted[loc_nan]     = distr.ppf(params[loc_nan], sample[loc_nan]).flatten()
        converted[loc_not_nan] = convert_sample_to_truncated_triang(params[loc_not_nan], sample[loc_not_nan]).flatten()
        return converted
    else:
        return distr.ppf(params, sample)


