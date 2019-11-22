import numpy as np
import brightway2 as bw
from pypardiso import spsolve

# This script peforms MonteCarlo simulations using presamples.

def find_where_in_techparams(cge_parameters_sto, lca):
    
    mask_tech = lambda inp, out: np.where(np.all([lca.tech_params['row']==inp, 
                                                  lca.tech_params['col']==out],axis=0)) [0][0]

    mask_bio  = lambda inp, out: np.where(np.all([lca.bio_params['row'] ==inp, 
                                                  lca.bio_params['col'] ==out],axis=0)) [0][0]

    n_parameters = len(cge_parameters_sto)
    where_tech = np.array([], dtype=int)
    amt_tech = np.array([])
    where_bio  = np.array([], dtype=int)
    amt_bio = np.array([])
    for j in range(n_parameters):
        if cge_parameters_sto[j][0][0] != 'biosphere3':
            input_  = lca.activity_dict[cge_parameters_sto[j][0]]
            output_ = lca.activity_dict[cge_parameters_sto[j][1]]
            temp = mask_tech(input_, output_)
            where_tech = np.append(where_tech, temp)
            amt_tech = np.append(amt_tech, cge_parameters_sto[j][2])
        else:
            input_  = lca.biosphere_dict[cge_parameters_sto[j][0]]
            output_ = lca.activity_dict[cge_parameters_sto[j][1]]
            temp = mask_bio(input_, output_)
            where_bio = np.append(where_bio, temp)
            amt_bio = np.append(amt_bio, cge_parameters_sto[j][2])
    
    if amt_tech.shape[0] != 0:
        amt_tech = amt_tech.reshape([len(where_tech),-1])
    if amt_bio.shape[0] != 0:
        amt_bio  = amt_bio.reshape([len(where_bio),-1])
    
    return where_tech, amt_tech, where_bio, amt_bio



def run_mc(parameters, demand , methods, n_iter):
    
    # Parameters has the format presamples, and is the outpuyt from cge or ege model.
    
    lca = bw.LCA({demand:1}, )
    lca.lci()
    lca.build_demand_array()
    demand_array = lca.demand_array
    tech_params = lca.tech_params['amount']
    bio_params = lca.bio_params['amount']

    where_tech, amt_tech, where_bio, amt_bio = find_where_in_techparams(parameters, lca)         
    
    scores = {}
    
    # This enables the code to work if only one method is passed as tuple
    if type(methods) == tuple:
        methods = [methods]
         
    for method in methods:
        
        lca.switch_method(method)
        CF_matr = sum(lca.characterization_matrix) 
        
        scores_m = np.zeros(n_iter)
        
        for i in range(n_iter):

            if where_tech.shape[0] != 0:
                np.put(tech_params, where_tech, amt_tech[:,i])
                lca.rebuild_technosphere_matrix(tech_params)

            if where_bio.shape[0] != 0:
                np.put(bio_params, where_bio, amt_bio[:,i])
                lca.rebuild_biosphere_matrix(bio_params)

            score = (CF_matr*lca.biosphere_matrix) * \
                     spsolve(lca.technosphere_matrix, demand_array)
            scores_m[i] = score
            
        scores[method] = scores_m
        
    return scores