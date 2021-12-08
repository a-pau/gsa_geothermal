import os, pickle
from copy import deepcopy
import brightway2 as bw
import numpy as np

# Local files
from gsa_geothermal.utils.lookup_func import lookup_geothermal
from gsa_geothermal.parameters import get_parameters
from gsa_geothermal.general_models import GeothermalConventionalModel, GeothermalEnhancedModel
from pypardiso import spsolve


def setup_gsa_problem(n_dimensions):
    calc_second_order = False
    problem = {
      'num_vars': n_dimensions,
      'names':    np.arange(n_dimensions),
      'bounds':   np.array([[0,1]]*n_dimensions)
    }
    return problem, calc_second_order


def setup_geothermal(project, option, flag_diff_distributions=False):
    # Project
    bw.projects.set_current(project)
    # Demand
    _, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_prod_conventional, electricity_prod_enhanced = lookup_geothermal()
    # Which parameters to choose
    if flag_diff_distributions:
        cge_parameters = get_parameters("conventional.diff_distributions")
        ege_parameters = get_parameters("enhanced.diff_distributions")
    else:
        cge_parameters = get_parameters("conventional")
        ege_parameters = get_parameters("enhanced")
    # Select all for conventional or enhanced
    if option == "conventional":
        demand = electricity_prod_conventional
        parameters = cge_parameters
        GeothermalModel = GeothermalConventionalModel
    elif option == "enhanced":
        demand = electricity_prod_enhanced
        parameters = ege_parameters
        GeothermalModel = GeothermalEnhancedModel
    else:
        print("Choose {} as `conventional` or `enhanced`")
        return
    geothermal_model = GeothermalModel(parameters)
    return demand, geothermal_model, parameters




def gen_characterization_matrices(lca, methods):
    method_matrices = []
    for method in methods:
        lca.switch_method(method)
        method_matrices.append(lca.characterization_matrix)
    return method_matrices


def get_lcia_results(path):
    """TODO Sasha change os to pathlib"""
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) 
             and 'all' not in f and 'scores' in f]
    starts = [int(f.split('_')[1]) for f in files]
    ind_sort = np.argsort(starts)
    files_sorted = [files[i] for i in ind_sort]
    scores = []
    for file in files_sorted:
        filepath = os.path.join(path,file)
        with open(filepath, 'rb') as f:
            scores.append(pickle.load(f))
    return np.vstack(np.array(scores))


def setup_project(option):
    project = 'Geothermal'
    demand, geothermal_model, parameters = setup_geothermal(project, option)
    methods = get_ILCD_methods()

    lca = bw.LCA(demand, methods[0])
    lca.lci()
    lca.lcia()
    lca.build_demand_array()
    gsa_in_lca = GSAinLCA(lca, parameters, geothermal_model, project = project)

    num_vars = len(gsa_in_lca.parameters_array) \
             + len(gsa_in_lca.uncertain_exchanges_dict['tech_params_where']) \
             + len(gsa_in_lca.uncertain_exchanges_dict['bio_params_where'])
    problem, calc_second_order = setup_gsa_problem(num_vars)
    parameters_list = gsa_in_lca.parameters_array['name'].tolist()
    
    return problem, calc_second_order, parameters_list, methods



# ## Sobol indices computation ###

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

    return A,B,AB,BA


def first_order(A, AB, B):
    # First order estimator following Saltelli et al. 2010 CPC, normalized by
    # sample variance
    return np.mean(B * (AB - A), axis=0) / np.var(np.r_[A,B,AB], axis=0)
#     return np.mean(B * (AB - A), axis=0) # in the paper


def total_order(A, AB, B):
    # Total order estimator following Saltelli et al. 2010 CPC, normalized by
    # sample variance
    return 0.5 * np.mean((A - AB) ** 2, axis=0) / np.var(np.r_[A,AB], axis=0)
#     return 0.5 * np.mean((A - AB) ** 2, axis=0) # in the paper


def my_sobol_analyze(problem, Y, calc_second_order):
    
    D = problem['num_vars']
    if calc_second_order==False:
        N = Y.shape[0]//(D+2)
        
#     Y = (Y - Y.mean())/Y.std()
    
    A,B,AB,BA = separate_output_values(Y, D, N, calc_second_order)
    f = np.zeros(D)
    t = np.zeros(D)
    
    for j in range(D):
        t[j] = total_order(A, AB[:,j], B)
        f[j] = first_order(A, AB[:,j], B)
        
    dict_ = dict(S1=f, ST=t)
    
    return dict_


def find_where_in_techparams(cge_parameters_sto, lca):
    mask_tech = lambda inp, out: np.where(np.all([lca.tech_params['row'] == inp,
                                                  lca.tech_params['col'] == out], axis=0))[0][0]

    mask_bio = lambda inp, out: np.where(np.all([lca.bio_params['row'] == inp,
                                                 lca.bio_params['col'] == out], axis=0))[0][0]

    n_parameters = len(cge_parameters_sto)
    where_tech = np.array([], dtype=int)
    amt_tech = np.array([])
    where_bio = np.array([], dtype=int)
    amt_bio = np.array([])
    for j in range(n_parameters):
        if cge_parameters_sto[j][0][0] != 'biosphere3':
            input_ = lca.activity_dict[cge_parameters_sto[j][0]]
            output_ = lca.activity_dict[cge_parameters_sto[j][1]]
            temp = mask_tech(input_, output_)
            where_tech = np.append(where_tech, temp)
            amt_tech = np.append(amt_tech, cge_parameters_sto[j][2])
        else:
            input_ = lca.biosphere_dict[cge_parameters_sto[j][0]]
            output_ = lca.activity_dict[cge_parameters_sto[j][1]]
            temp = mask_bio(input_, output_)
            where_bio = np.append(where_bio, temp)
            amt_bio = np.append(amt_bio, cge_parameters_sto[j][2])

    if amt_tech.shape[0] != 0:
        amt_tech = amt_tech.reshape([len(where_tech), -1])
    if amt_bio.shape[0] != 0:
        amt_bio = amt_bio.reshape([len(where_bio), -1])

    return where_tech, amt_tech, where_bio, amt_bio


def run_mc(parameters, demand, methods, n_iter):
    # Parameters has the format presamples, and is the output from cge or ege model.

    assert n_iter == len(parameters[0][2])

    lca = bw.LCA(demand)
    lca.lci()
    lca.build_demand_array()
    demand_array = lca.demand_array
    tech_params = lca.tech_params['amount']
    bio_params = lca.bio_params['amount']

    method_matrices = gen_characterization_matrices(lca, methods)
    CF_matr = [sum(m) for m in method_matrices]

    where_tech, amt_tech, where_bio, amt_bio = find_where_in_techparams(parameters, lca)

    scores = {}

    # This enables the code to work if only one method is passed as tuple
    if type(methods) == tuple:
        methods = [methods]

    nan_array = np.empty(n_iter)
    nan_array[:] = np.nan
    scores = {method[-1]: deepcopy(nan_array) for method in methods}

    for i in range(n_iter):

        if where_tech.shape[0] != 0:
            np.put(tech_params, where_tech, amt_tech[:, i])
            lca.rebuild_technosphere_matrix(tech_params)

        if where_bio.shape[0] != 0:
            np.put(bio_params, where_bio, amt_bio[:, i])
            lca.rebuild_biosphere_matrix(bio_params)

        # scores_m = np.zeros(parameters.iterations)
        for i_method, method in enumerate(methods):
            lca.switch_method(method)
            score = (CF_matr[i_method] * lca.biosphere_matrix) * \
                    spsolve(lca.technosphere_matrix, demand_array)
            scores[method[-1]][i] = score

        # scores[method[-1]] = scores_m
    return scores



