import brightway2 as bw
import numpy as np
import os, pickle



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




