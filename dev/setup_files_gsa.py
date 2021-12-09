from copy import deepcopy
import brightway2 as bw
import numpy as np

# Local files
from pypardiso import spsolve




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



