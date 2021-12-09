# import bw2calc as bc
import numpy as np
# import pickle
# from SALib.sample import saltelli

# Local files
# from ..global_sensitivity_analysis import GSAinLCA


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
