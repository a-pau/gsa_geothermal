import brightway2 as bw
import numpy as np
import os, pickle
from utils.gsa_lca_dask import *



def setup_gsa(n_dimensions):
    calc_second_order = False
    problem = {
      'num_vars': n_dimensions,
      'names':    np.arange(n_dimensions),
      'bounds':   np.array([[0,1]]*n_dimensions)
    }
    return problem, calc_second_order


def setup_gt_project(project, option):
    
    bw.projects.set_current(project)
    
    #Local files
    from utils.lookup_func import lookup_geothermal

    #Choose demand/
    _, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_prod_conv, electricity_prod_enha = lookup_geothermal()

     #Choose LCIA methods
    ILCD_CC = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)]
    ILCD_HH = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "human health" in str(method)]
    ILCD_EQ = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "ecosystem quality" in str(method)]
    ILCD_RE = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "resources" in str(method)]
    methods = ILCD_CC + ILCD_HH + ILCD_EQ + ILCD_RE

    if option == 'cge':
        demand = {electricity_prod_conv: 1}
        from cge_klausen import parameters
        from cge_model import GeothermalConventionalModel as GTModel
    elif option == 'ege':
        demand = {electricity_prod_enha: 1}
        from ege_klausen import parameters
        from ege_model import GeothermalEnhancedModel as GTModel
        
    gt_model = GTModel(parameters)

    return demand, methods, gt_model, parameters


def gen_cf_matrices(lca, methods):
    method_matrices = []
    for method in methods:
        lca.switch_method(method)
        method_matrices.append(lca.characterization_matrix)
        
    return method_matrices


def get_lcia_results(path):
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


def setup_all(option):
    project = 'Geothermal'

    demand, methods, gt_model, parameters = setup_gt_project(project, option)

    lca = bw.LCA(demand, methods[0])
    lca.lci()
    lca.lcia()
    lca.build_demand_array()
    gsa_in_lca = GSAinLCA(lca, parameters, gt_model, project = project)

    num_vars = len(gsa_in_lca.parameters_array) \
             + len(gsa_in_lca.uncertain_exchanges_dict['tech_params_where']) \
             + len(gsa_in_lca.uncertain_exchanges_dict['bio_params_where'])
    problem, calc_second_order = setup_gsa(num_vars)
    parameters_list = gsa_in_lca.parameters_array['name'].tolist()
    
    return problem, calc_second_order, parameters_list, methods



### Sobol indices computation ###

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






