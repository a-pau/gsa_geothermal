import bw2data as bd
import bw2calc as bc
import numpy as np
import pickle
from SALib.sample import saltelli

from gsa_geothermal.utils import lookup_geothermal, get_EF_methods
from gsa_geothermal.parameters import get_parameters
from gsa_geothermal.general_models import GeothermalConventionalModel, GeothermalEnhancedModel
from gsa_geothermal.global_sensitivity_analysis import GSAinLCA, model_per_X_chunk, gen_characterization_matrices


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


def setup_geothermal_gsa(option):
    project = 'Geothermal'
    demand_act, gt_model, parameters = setup_geothermal(project, option)
    methods = get_EF_methods()
    lca = bc.LCA({demand_act: 1}, methods[0])
    lca.lci()
    lca.lcia()
    lca.build_demand_array()
    gsa_in_lca = GSAinLCA(project, lca, parameters, gt_model)
    num_vars = (
            len(gsa_in_lca.parameters_array) +
            len(gsa_in_lca.uncertain_exchanges_dict['tech_params_where']) +
            len(gsa_in_lca.uncertain_exchanges_dict['bio_params_where'])
    )
    problem, calc_second_order = setup_gsa_problem(num_vars)
    parameters_list = gsa_in_lca.parameters_array['name'].tolist()
    return problem, calc_second_order, parameters_list, methods


def task_per_worker(
        project,
        iterations,
        option,
        n_workers,
        i_chunk,
        path_files,
        diff_distr,
):

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