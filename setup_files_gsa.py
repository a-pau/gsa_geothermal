import os, pickle
from copy import deepcopy
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

    # Demand
    _, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_prod_conv, electricity_prod_enha = lookup_geothermal()   
       
    if option == 'cge':
        demand = {electricity_prod_conv: 1}
        from cge_klausen import get_parameters
        parameters = get_parameters()
        from cge_model import GeothermalConventionalModel as GTModel
    elif option == 'ege':
        demand = {electricity_prod_enha: 1}
        from ege_klausen import get_parameters
        parameters = get_parameters()
        from ege_model import GeothermalEnhancedModel as GTModel
        
    gt_model = GTModel(parameters)

    return demand, gt_model, parameters

def get_ILCD_methods(CC_only=False, units=False):
    
    # ILCD-EF2.0 methods
    ILCD_CC = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)]
    ILCD_HH = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "human health" in str(method)]
    ILCD_EQ = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "ecosystem quality" in str(method)]
    ILCD_RE = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "resources" in str(method)]
    
    # Adjust units
    adjust_units_dict = {
        'kg NMVOC-.': 'kg NMVOC-Eq',
        'm3 water-.' : 'm3 water world-Eq',
        'CTU' : 'CTUe',
        'kg CFC-11.' : 'kg CFC-11-Eq',
        'megajoule': 'MJ'}
    
    if CC_only:
        methods = ILCD_CC
    else:
        methods = ILCD_CC + ILCD_HH + ILCD_EQ + ILCD_RE
     
    if units:
        temp=[bw.methods[method]["unit"] for method in methods]
        ILCD_units=[adjust_units_dict[elem] if elem in adjust_units_dict else elem for elem in temp]        
        return methods, ILCD_units
    else:
        return methods 

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

    demand, gt_model, parameters = setup_gt_project(project, option)
    methods = get_ILCD_methods()

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

    method_matrices = gen_cf_matrices(lca, methods)
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



