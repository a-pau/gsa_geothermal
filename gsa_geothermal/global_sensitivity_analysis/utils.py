import bw2calc as bc
import numpy as np
from copy import deepcopy
from pypardiso import spsolve


def gen_characterization_matrices(lca, methods):
    method_matrices = []
    for method in methods:
        lca.switch_method(method)
        method_matrices.append(lca.characterization_matrix)
    return method_matrices


def model_per_X_chunk(X_chunk, gsa_in_lca, method_matrices):
    scores = []
    i = 0
    for sample in X_chunk:
        score = gsa_in_lca.model(sample, method_matrices)
        scores.append(score)
        i += 1
    return np.array(scores)


def separate_output_values(Y, D, N, calc_second_order):
    AB = np.zeros((N, D))
    BA = np.zeros((N, D)) if calc_second_order else None
    step = 2 * D + 2 if calc_second_order else D + 2

    A = Y[0:Y.size:step]
    B = Y[(step - 1):Y.size:step]
    for j in range(D):
        AB[:, j] = Y[(j + 1):Y.size:step]
        if calc_second_order:
            BA[:, j] = Y[(j + 1 + D):Y.size:step]

    return A, B, AB, BA


def first_order(A, AB, B):
    # First order estimator following Saltelli et al. 2010 CPC, normalized by
    # sample variance
    return np.mean(B * (AB - A), axis=0) / np.var(np.r_[A, B, AB], axis=0)
#     return np.mean(B * (AB - A), axis=0) # in the paper


def total_order(A, AB, B):
    # Total order estimator following Saltelli et al. 2010 CPC, normalized by
    # sample variance
    return 0.5 * np.mean((A - AB) ** 2, axis=0) / np.var(np.r_[A, AB], axis=0)
#     return 0.5 * np.mean((A - AB) ** 2, axis=0) # in the paper


def my_sobol_analyze(problem, Y, calc_second_order):

    D = problem['num_vars']
    if not calc_second_order:
        N = Y.shape[0]//(D+2)

    #     Y = (Y - Y.mean())/Y.std()

    A, B, AB, BA = separate_output_values(Y, D, N, calc_second_order)
    f = np.zeros(D)
    t = np.zeros(D)

    for j in range(D):
        t[j] = total_order(A, AB[:, j], B)
        f[j] = first_order(A, AB[:, j], B)

    dict_ = dict(S1=f, ST=t)

    return dict_


def find_where_in_techparams(parameters, lca):

    def get_mask_tech(lca_, in_, out):
        mask = np.where(
            np.all(
                [
                    lca_.tech_params['row'] == in_,
                    lca_.tech_params['col'] == out,
                ],
                axis=0
            )
        )[0][0]
        return mask

    def get_mask_bio(lca_, in_, out):
        mask = np.where(
            np.all(
                [
                    lca_.bio_params['row'] == in_,
                    lca_.bio_params['col'] == out,
                ],
                axis=0
            )
        )[0][0]
        return mask

    n_parameters = len(parameters)
    where_tech = np.array([], dtype=int)
    amt_tech = np.array([])
    where_bio = np.array([], dtype=int)
    amt_bio = np.array([])
    for j in range(n_parameters):
        if parameters[j][0][0] != 'biosphere3':
            input_ = lca.activity_dict[parameters[j][0]]
            output_ = lca.activity_dict[parameters[j][1]]
            mask_ = get_mask_tech(lca, input_, output_)
            where_tech = np.append(where_tech, mask_)
            amt_tech = np.append(amt_tech, parameters[j][2])
        else:
            input_ = lca.biosphere_dict[parameters[j][0]]
            output_ = lca.activity_dict[parameters[j][1]]
            mask_ = get_mask_bio(lca, input_, output_)
            where_bio = np.append(where_bio, mask_)
            amt_bio = np.append(amt_bio, parameters[j][2])

    if amt_tech.shape[0] != 0:
        amt_tech = amt_tech.reshape([len(where_tech), -1])
    if amt_bio.shape[0] != 0:
        amt_bio = amt_bio.reshape([len(where_bio), -1])

    return where_tech, amt_tech, where_bio, amt_bio


def run_monte_carlo(parameters, demand, methods, iterations):
    """Parameters has the format presamples, and is the output from cge or ege model."""

    assert iterations == len(parameters[0][2])

    lca = bc.LCA(demand)
    lca.lci()
    lca.build_demand_array()
    demand_array = lca.demand_array
    tech_params = lca.tech_params['amount']
    bio_params = lca.bio_params['amount']

    method_matrices = gen_characterization_matrices(lca, methods)
    characterization_matrices = [sum(m) for m in method_matrices]

    where_tech, amt_tech, where_bio, amt_bio = find_where_in_techparams(parameters, lca)

    # This enables the code to work if only one method is passed as tuple
    if type(methods) == tuple:
        methods = [methods]

    nan_array = np.empty(iterations)
    nan_array[:] = np.nan
    scores = {method[-2]: deepcopy(nan_array) for method in methods}

    for i in range(iterations):

        if where_tech.shape[0] != 0:
            np.put(tech_params, where_tech, amt_tech[:, i])
            lca.rebuild_technosphere_matrix(tech_params)

        if where_bio.shape[0] != 0:
            np.put(bio_params, where_bio, amt_bio[:, i])
            lca.rebuild_biosphere_matrix(bio_params)

        # scores_m = np.zeros(parameters.iterations)
        for i_method, method in enumerate(methods):
            lca.switch_method(method)
            score = (
                (characterization_matrices[i_method] * lca.biosphere_matrix) *
                spsolve(lca.technosphere_matrix, demand_array)
            )
            scores[method[-2]][i] = score

    return scores
