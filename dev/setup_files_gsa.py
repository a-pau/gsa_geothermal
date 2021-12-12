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







