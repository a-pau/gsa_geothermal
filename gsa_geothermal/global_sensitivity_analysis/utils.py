import bw2data as bd
import bw2calc as bc
import numpy as np
import pickle
from SALib.sample import saltelli

# Local files
from ..parameters import get_parameters
from ..general_models import GeothermalConventionalModel,  GeothermalEnhancedModel
from ..import_database import get_EF_methods
from ..global_sensitivity_analysis import GSAinLCA
from ..utils import lookup_geothermal


def gen_characterization_matrices(lca, methods):
    method_matrices = []
    for method in methods:
        lca.switch_method(method)
        method_matrices.append(lca.characterization_matrix)
    return method_matrices


def setup_geothermal(project, option, flag_diff_distributions=False):
    # Project
    bd.projects.set_current(project)
    # Demand
    _, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_prod_conventional, electricity_prod_enhanced \
        = lookup_geothermal()
    # Which parameters to choose
    if flag_diff_distributions:
        parameters = get_parameters("{}.diff_distributions".format(option))
    else:
        parameters = get_parameters(option)
    # Select all for conventional or enhanced
    if option == "conventional":
        demand = electricity_prod_conventional
        GeothermalModel = GeothermalConventionalModel
    elif option == "enhanced":
        demand = electricity_prod_enhanced
        GeothermalModel = GeothermalEnhancedModel
    else:
        print("Choose {} as `conventional` or `enhanced`")
        return
    geothermal_model = GeothermalModel(parameters)
    return demand, geothermal_model, parameters


def setup_gsa_problem(n_dimensions):
    calc_second_order = False
    problem = {
        'num_vars': n_dimensions,
        'names':    np.arange(n_dimensions),
        'bounds':   np.array([[0, 1]]*n_dimensions)
    }
    return problem, calc_second_order


def model_per_X_chunk(X_chunk, gsa_in_lca, method_matrices):
    scores = []
    i = 0
    for sample in X_chunk:
        score = gsa_in_lca.model(sample, method_matrices)
        scores.append(score)
        i += 1
    return np.array(scores)


def task_per_worker(project, iterations, option, n_workers, i_chunk, path_files, diff_distr):

    # 1. setup geothermal project
    demand_act, gt_model, parameters = setup_geothermal(project, option, flag_diff_distributions=diff_distr)
    methods = get_EF_methods(select_climate_change_only=False, return_units=False)

    # 2. generate characterization matrices for all methods
    lca = bc.LCA({demand_act: 1}, methods[0])
    lca.lci(factorize=True)
    lca.lcia()
    lca.build_demand_array()
    method_matrices = gen_characterization_matrices(lca, methods)

    # 3. gsa in lca model
    gsa_in_lca = GSAinLCA(
        project=project,
        lca=lca,
        parameters=parameters,
        parameters_model=gt_model,
    )

    # 4. setup GSA project in the SALib format
    num_vars = (
        len(gsa_in_lca.parameters_array) +
        len(gsa_in_lca.uncertain_exchanges_dict['tech_params_where']) +
        len(gsa_in_lca.uncertain_exchanges_dict['bio_params_where'])
    )
    problem, calc_second_order = setup_gsa_problem(num_vars)

    # 5. generate sobol samples, choose correct chunk for the current worker based on index i_chunk
    X = saltelli.sample(problem, iterations, calc_second_order=calc_second_order)

    # 6. Extract part of the sample for the current worker
    chunk_size = X.shape[0]//n_workers
    start = i_chunk*chunk_size
    if i_chunk != n_workers-1:
        end = (i_chunk+1)*chunk_size
    else:
        end = X.shape[0]
    X_chunk = X[start:end, :]
    del X

    # 6. compute scores for all methods for X_chunk
    scores_for_methods = model_per_X_chunk(X_chunk, gsa_in_lca, method_matrices)

    # 7. Save results
    filepath = path_files / 'scores_{}_{}.pickle'.format(start, end-1)
    with open(filepath, "wb") as fp:
        pickle.dump(scores_for_methods, fp)

    return scores_for_methods


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
        t[j] = total_order(A, AB[:,j], B)
        f[j] = first_order(A, AB[:,j], B)

    dict_ = dict(S1=f, ST=t)

    return dict_
