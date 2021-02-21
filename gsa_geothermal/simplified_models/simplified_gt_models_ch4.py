# import pandas as pd
# import os, json

import numpy as np
from copy import deepcopy
from sympy import symbols, collect, ratsimp, fraction


# Local
from setup_files_gsa import *
from utils.lookup_func import lookup_geothermal


################################################
### Geothermal simplified model PARENT class ###
################################################

class GeothermalSimplifiedModel:

    def __init__(self, option, threshold, exploration, path=None):
        self.option = option
        self.threshold = threshold
        if path == None:
            path = 'generated_files/gsa_results/' + option + '_N500/'
        total_df = self.get_total_indices(path)
        self.total_df = total_df
        self.methods_groups = self.get_methods_groups(total_df, self.threshold)
        self.i_coeff_matrix = self.compute_i_coeff()
        self.impact = self.define_symbolic_eq()
        self.exploration = exploration
        
        self.correspondence_dict = {
            'co2_emissions': 'E_co2',
            'gross_power_per_well': 'CW_ne',
            'average_depth_of_wells': 'W_d',
            'initial_harmonic_decline_rate': 'D_i',
            'success_rate_primary_wells': 'SR_p',
            'installed_capacity': 'P_ne',
            'specific_diesel_consumption': 'D',
        }
        
    def get_total_indices(self, path):
        '''
        :param path: give path to files with total order indices
        :return:
        '''
        problem, calc_second_order, parameters_list, methods = setup_all(self.option)
        self.methods = methods

        scores = get_lcia_results(path)
        sa_dict = dict(parameters=parameters_list)
        for i, method in enumerate(methods):
            method_name = method[-1]
            Y = scores[:, i]
            sa_dict[method_name] = my_sobol_analyze(problem, Y, calc_second_order)

        # Extract total index into a dictionary and dataframe
        total_dict = {}
        total_dict['parameters'] = parameters_list
        total_dict.update({
            k: v['ST'] for k, v in sa_dict.items() if k != 'parameters'
        })
        total_df = pd.DataFrame(total_dict)
        total_df = total_df.set_index('parameters')
        return total_df

    def get_methods_groups(self, total_df, threshold):
        '''
        get methods groups for only one threshold
        :return:
        '''
        # Identify values above threshold
        mask = np.array(total_df.values >= threshold, dtype=int)
        total_df_mask = pd.DataFrame(mask)
        total_df_mask.columns = total_df.columns
        total_df_mask.index = total_df.index
        # Identify influential parameters
        df_use_params = total_df_mask.loc[(total_df_mask != 0).any(axis=1)]
        # Form groups of methods based on which influential parameters they need
        unique_method_groups = np.unique(df_use_params.values, axis=1)
        # Construct a dictionary with groups of methods and their respective influential parameters
        methods_groups = []
        for i, u in enumerate(unique_method_groups.T):
            list_ = []
            for col in df_use_params.columns:
                if np.all(df_use_params[col].values == u):
                    list_.append(col)

            methods_groups.append({
                'parameters': list(df_use_params.index.values[np.where(u != 0)[0]]),
                'methods': list_,
            })

        return methods_groups

    def compute_i_coeff(self):
        # Retrieve activities
        wellhead, diesel, steel, cement, water, \
        drilling_mud, drill_wst, wells_closr, coll_pipe, \
        plant, ORC_fluid, ORC_fluid_wst, diesel_stim, co2, _, _ = lookup_geothermal()
        cooling_tower = bw.Database("geothermal energy").search("cooling tower")[0].key

        list_act = [wellhead, diesel, steel, cement, water,
                    drilling_mud, drill_wst, wells_closr, coll_pipe,
                    plant, cooling_tower, ORC_fluid, ORC_fluid_wst, diesel_stim]

        # Calculate impact of activities
        lca = bw.LCA({list_act[0]: 1}, self.methods[0])
        lca.lci()
        lca.lcia()
        coeff = {}
        for method in self.methods:
            s = []
            lca.switch_method(method)
            for act in list_act:
                lca.redo_lcia({act: 1})
                s.append(lca.score)
            coeff[method[-1]] = s

        # Retrieve CF for co2 emissions
        for method in self.methods:
            CFs = bw.Method(method).load()
            coeff[method[-1]].append(next((cf[1] for cf in CFs if cf[0] == co2), 0))

        # Build matrix
        col_names = ["wellhead", "diesel", "steel", "cement", "water", \
                     "drilling_mud", "drill_wst", "wells_closr", "coll_pipe", \
                     "plant", "cooling tower", "ORC_fluid", "ORC_fluid_wst", "diesel_stim", "co2"]
        i_coeff_matrix = pd.DataFrame.from_dict(coeff, orient="index", columns=col_names)

        # Re-arrange matrix
        i_coeff_matrix["concrete"] = i_coeff_matrix["cement"] + i_coeff_matrix["water"] * 1 / 0.65
        i_coeff_matrix["ORC_fluid_tot"] = i_coeff_matrix["ORC_fluid"] - i_coeff_matrix["ORC_fluid_wst"]
        i_coeff_matrix["electricity_stim"] = i_coeff_matrix["diesel_stim"] * 3.6
        i_coeff_matrix["drill_wst"] = i_coeff_matrix["drill_wst"] * -1
        i_coeff_matrix = i_coeff_matrix.drop(columns=["cement", "ORC_fluid", "ORC_fluid_wst", "diesel_stim"])

        col_ord = ["wellhead", "diesel", "steel", "concrete", \
                   "drilling_mud", "drill_wst", "wells_closr", "coll_pipe", \
                   "plant", "cooling tower", "ORC_fluid_tot", "water", "electricity_stim", "co2"]
        i_coeff_matrix = i_coeff_matrix[col_ord]

        is_ = ["i1", "i2_1", "i2_2", "i2_3", "i2_4", "i2_5", \
               "i2_6", "i3", "i4_1", "i4_2", "i4_3", "i5_1", "i5_2", "i6"]

        if len(i_coeff_matrix.columns) == len(is_):
            i_coeff_matrix.columns = is_

        return i_coeff_matrix   
    
    def define_symbolic_eq(self):
        ### 1. Main parameters as in Table 1 of the paper
        # Power plant
        P_ne, AP, CF, LT, CP, E_co2 = symbols('P_ne, AP, CF, LT, CP, E_co2')
        # Wells
        CW_ne, W_d, D, Cs, Cc, DM, D_i, PIratio = symbols('CW_ne, W_d, D, Cs, Cc, DM, D_i, PIratio')
        # Success rate
        SR_e, SR_p, SR_m = symbols('SR_e, SR_p, SR_m')
        # Stimulation
        S_w, S_el, SW_n = symbols('S_w, S_el, SW_n')
        ### 2. Fixed parameters as in Table 2 of the paper
        W_en, OF, CT_n, DW = symbols('W_en, OF, CT_n, DW')
        ### 3. `i` Coefficients
        i1, i2_1, i2_2, i2_3, i2_4, i2_5, i2_6, i3, i4_1, i4_2, i4_3, i5_1, i5_2, i6 = \
            symbols('i1, i2_1, i2_2, i2_3, i2_4, i2_5, i2_6, i3, i4_1, i4_2, i4_3, i5_1, i5_2, i6')

        ### Total number of wells with success rate
        if self.option == 'cge':
            W_Pn = P_ne / CW_ne  # production wells
            W_n_sr = W_Pn * ((1 + 1 / PIratio) / (SR_p/100) + D_i * LT / (SR_m/100))
            W_n = W_Pn * ((1 + 1 / PIratio) + D_i * LT)
        elif self.option == 'ege':
            W_Pn = symbols('W_Pn')
            W_n_sr = W_Pn / (SR_p/100)
            W_n = W_Pn

        W_E_en_sr = W_en * 0.3 / (SR_e/100)
        W_E_en = W_en * 0.3

        ### Impacts of each component from Equation 1
        wells = (W_n + W_E_en) * i1 +\
                (W_n_sr + W_E_en_sr) * W_d * (D * i2_1 + Cs * i2_2 + Cc * i2_3 + DM * i2_4 + DW * i2_5 + i2_6)
        collection_pipelines = W_n * CP * i3
        power_plant = P_ne * (i4_1 + CT_n * i4_2 + OF * i4_3)
        stimulation = SW_n * S_w * (i5_1 + S_el * i5_2) # NO W_n here, because it is included in SW_n
        operational_emissions = E_co2 * i6
        lifetime = P_ne * CF * (1 - AP) * LT * 8760 * 1000

        ### Main equation
        impact = (wells + collection_pipelines + power_plant + stimulation) / lifetime + \
                 operational_emissions

        return impact

    def get_par_dict(self, parameters):
        '''
        Substitution dictionary for symbolic subs
        :param parameters:
        :return:
        '''
        # Fixed values of the parameters that are common to enhanced and conventional
        par_dict = dict(
            # Power plant
            P_ne=parameters["installed_capacity"],
            AP=parameters["auxiliary_power"],
            CF=parameters["capacity_factor"],
            LT=parameters["lifetime"],
            CP=parameters["collection_pipelines"],
            # Wells
            W_d=parameters["average_depth_of_wells"],
            D=parameters["specific_diesel_consumption"],
            Cs=parameters["specific_steel_consumption"],
            Cc=parameters["specific_cement_consumption"],
            DM=parameters["specific_drilling_mud_consumption"],
            # Success rate
            SR_e=parameters["success_rate_exploration_wells"],
            SR_p=parameters["success_rate_primary_wells"],
            # Constants
            CT_n=7 / 303.3,
            DW=450,
        )
        
        if self.exploration == True:
            par_dict.update(dict(W_en=3)) 
        elif self.exploration == False:
            # Note, W_en can't be zero because chi 5% equations won't work.
            par_dict.update(dict(W_en=0.00001)) 
            
            
        return par_dict

    def run(self, parameters_sto, simplified_model_dict, lcia_methods=None, ch4=False):
        '''
        Run simplified model
        :param parameters: can be static or stochastic
        :param lcia_methods: in case you're only interested in a subset of methods
        :return: results of the simplified model
        '''
        if lcia_methods == None:
            lcia_methods = self.methods
        
        results = {}
        for method in lcia_methods:
            s_const = simplified_model_dict[method[-1]]['s_const']
            if ch4 and method[-1] == "climate change total":
                s_model = simplified_model_dict[method[-1]]['s_model_ch4']
            else:
                s_model = simplified_model_dict[method[-1]]['s_model']
                
            res = s_model(s_const, parameters_sto)

            if isinstance(res, np.ndarray):
                res = res.astype("float")
            else:
                res = float(res)
            
            results[method[-1]] = res

        return results

    def get_coeff(self, simplified_model_dict, lcia_methods=None):

        if lcia_methods == None:
            lcia_methods = self.methods

        coeff = {}
        for method in lcia_methods:
            coeff[method[-1]] = simplified_model_dict[method[-1]]['s_const']

        return coeff


#################################################
### Conventional simplified model CHILD class ###
#################################################

class ConventionalSimplifiedModel(GeothermalSimplifiedModel):

    def __init__(self, threshold, exploration=True):
        super(ConventionalSimplifiedModel, self).__init__(option='cge', threshold=threshold, exploration=exploration)
        self.i_coeff_matrix['i5_1'] = 0
        self.i_coeff_matrix['i5_2'] = 0
        from cge_klausen import get_parameters
        parameters = get_parameters()
        parameters.static()
        self.par_subs_dict = self.get_par_dict(parameters)
        self.complete_par_dict(parameters)
        self.ch4_CF = self.get_ch4_CF()
        self.simplified_model_dict = self.get_simplified_model()   
    
        
    def get_ch4_CF(self):
        db_biosph = bw.Database("biosphere3")
        ch4  = [act for act in db_biosph if 'Methane, fossil' == act['name']
                and 'air' in act['categories'] 
                and 'low' not in str(act['categories'])
                and 'urban' not in str(act['categories'])][0].key
        
        ILCD_CC = get_ILCD_methods(CC_only=True)[0]
        ch4_CF = [cf[1] for cf in bw.Method(ILCD_CC).load() if cf[0] == ch4][0]
        
        return ch4_CF
    
    def complete_par_dict(self, parameters):
        '''
        Add values to a substitution dictionary that are CGE specific
        :param parameters:
        :return:
        '''
        self.par_subs_dict.update(dict(
            # Wells
            CW_ne=parameters["gross_power_per_well"],
            D_i=parameters["initial_harmonic_decline_rate"],
            PIratio=parameters["production_to_injection_ratio"],
            # Success rate
            SR_m=parameters["success_rate_makeup_wells"],
            # Operational CO2 emissions
            E_co2=parameters["co2_emissions"],
            # Constants
            OF=0
        ))

    def get_simplified_model(self):
        '''
        Compute constants (alpha, beta) and an expression for the simplified model
        :return:
        '''
        simplified_model_dict = {}

        for group in self.methods_groups:
            inf_params = group['parameters']
            par_dict_copy = deepcopy(self.par_subs_dict)
            [par_dict_copy.pop(self.correspondence_dict[p]) for p in inf_params]

            # Alphas all thresholds
            if set(inf_params) == {'co2_emissions'}:
                E_co2 = symbols('E_co2')
                impact_copy = deepcopy(self.impact.subs(par_dict_copy))
                alpha1 = collect(impact_copy, E_co2, evaluate=False)[E_co2]
                alpha2 = collect(impact_copy, E_co2, evaluate=False)[1]
                for method in group['methods']:
                    is_dict = dict(self.i_coeff_matrix.T[method])
                    alpha1_val = alpha1.subs(is_dict)
                    alpha2_val = alpha2.subs(is_dict)
                    simplified_model_dict[method] = {
                        's_const': {1: alpha1_val, 2: alpha2_val},
                        's_model': lambda alpha, parameters:
                        parameters['co2_emissions'] * alpha[1] + alpha[2],
                        's_model_ch4': lambda alpha, parameters:
                        parameters['co2_emissions'] * alpha[1] + alpha[2] + self.ch4_CF * parameters['ch4_emissions'],
                    }

            # Betas, 20/15%
            elif set(inf_params) == {'gross_power_per_well',
                                     'average_depth_of_wells'}:
                W_d, CW_ne = symbols('W_d, CW_ne')
                for method in group['methods']:
                    is_dict = dict(self.i_coeff_matrix.T[method])
                    impact_copy = deepcopy(self.impact.subs(par_dict_copy))
                    impact_copy = impact_copy.subs(is_dict)
                    impact_copy = ratsimp(impact_copy)
                    temp = collect(impact_copy, [W_d, 1 / CW_ne], evaluate=False)
                    temp2 = collect(temp[1 / CW_ne], W_d, evaluate=False)
                    beta1 = temp2[W_d]
                    beta2 = temp2[1]
                    beta3 = temp[W_d]
                    beta4 = temp[1]
                    simplified_model_dict[method] = {
                        's_const': {1: beta1, 2: beta2, 3: beta3, 4: beta4},
                        's_model': lambda beta, parameters:
                        (parameters['average_depth_of_wells'] * beta[1] + beta[2])
                        / parameters['gross_power_per_well']
                        + parameters['average_depth_of_wells'] * beta[3] + beta[4]
                    }

            # Betas, 10%
            elif set(inf_params) == {'gross_power_per_well',
                                     'average_depth_of_wells',
                                     'initial_harmonic_decline_rate'}:
                W_d, CW_ne, D_i = symbols('W_d, CW_ne, D_i')
                for method in group['methods']:
                    is_dict = dict(self.i_coeff_matrix.T[method])
                    impact_copy = deepcopy(self.impact.subs(par_dict_copy))
                    impact_copy = impact_copy.subs(is_dict)
                    impact_copy = ratsimp(impact_copy)
                    temp = collect(impact_copy, [1 / CW_ne, 1, W_d], evaluate=False)
                    temp2 = collect(temp[1 / CW_ne], [D_i * W_d, D_i, W_d, 1], evaluate=False)
                    beta1 = temp2[D_i * W_d]
                    beta2 = temp2[D_i]
                    beta3 = temp2[W_d]
                    beta4 = temp2[1]
                    beta5 = collect(temp[1], [W_d, 1], evaluate=False)[W_d]
                    beta6 = collect(temp[1], [W_d, 1], evaluate=False)[1]
                    simplified_model_dict[method] = {
                        's_const': {1: beta1, 2: beta2, 3: beta3, 4: beta4, 5: beta5, 6: beta6},
                        's_model': lambda beta, parameters:
                        (parameters['initial_harmonic_decline_rate'] * parameters['average_depth_of_wells'] * beta[1]
                         + parameters['initial_harmonic_decline_rate'] * beta[2]
                         + parameters['average_depth_of_wells'] * beta[3] + beta[4])
                        / parameters['gross_power_per_well']
                        + parameters['average_depth_of_wells'] * beta[5] + beta[6]
                    }

            # Betas, 5%
            elif set(inf_params) == {'gross_power_per_well',
                                     'average_depth_of_wells',
                                     'initial_harmonic_decline_rate',
                                     'success_rate_primary_wells'}:
                W_d, CW_ne, D_i, SR_p = symbols('W_d, CW_ne, D_i, SR_p')
                for method in group['methods']:
                    is_dict = dict(self.i_coeff_matrix.T[method])
                    impact_copy = deepcopy(self.impact.subs(par_dict_copy))
                    impact_copy = impact_copy.subs(is_dict)
                    impact_copy = ratsimp(impact_copy)
                    temp = collect(impact_copy, [1 / CW_ne*SR_p, 1], evaluate=False)
                    temp2 = collect(temp[list(temp.keys())[1]], [SR_p*W_d*D_i, D_i*SR_p, SR_p, W_d], evaluate=False)
                    beta1 = temp2[SR_p * D_i * W_d]
                    beta2 = temp2[D_i * SR_p]
                    beta3 = temp2[W_d]
                    beta4 = temp2[SR_p]
                    beta5 = collect(temp[1], [W_d, 1], evaluate=False)[W_d]
                    beta6 = collect(temp[1], [W_d, 1], evaluate=False)[1]
                    simplified_model_dict[method] = {
                        's_const': {1: beta1, 2: beta2, 3: beta3, 4: beta4, 5: beta5, 6: beta6},
                        's_model': lambda beta, parameters:
                        parameters['initial_harmonic_decline_rate'] * (
                                    parameters['average_depth_of_wells'] * beta[1] + beta[2])
                        / parameters['gross_power_per_well']
                        + (parameters['average_depth_of_wells'] * beta[3] + parameters['success_rate_primary_wells']*beta[4])
                        / parameters['gross_power_per_well'] / parameters['success_rate_primary_wells']
                        + parameters['average_depth_of_wells'] * beta[5] + beta[6]
                    }

        return simplified_model_dict

    def run(self, parameters, lcia_methods=None, ch4=False):
        return super().run(parameters, self.simplified_model_dict, lcia_methods, ch4)

    def get_coeff(self, lcia_methods=None):
        return super().get_coeff(self.simplified_model_dict, lcia_methods)


#############################################
### Enhanced simplified model CHILD class ###
#############################################

class EnhancedSimplifiedModel(GeothermalSimplifiedModel):

    def __init__(self, threshold, exploration=True):
        super(EnhancedSimplifiedModel, self).__init__(option='ege', threshold=threshold, exploration=exploration)
        self.i_coeff_matrix['i6'] = 0
        from ege_klausen import get_parameters
        parameters = get_parameters()
        parameters.static()  # TODO Remember to fix this
        self.par_subs_dict = self.get_par_dict(parameters)
        self.complete_par_dict(parameters)
        self.simplified_model_dict = self.get_simplified_model()

    def complete_par_dict(self, parameters):
        self.par_subs_dict.update(dict(
            # Wells
            W_Pn=parameters["number_of_wells"],
            # Stimulation
            S_w=parameters["water_stimulation"],
            S_el=parameters["specific_electricity_stimulation"] / 1000,
            SW_n=np.round(0.5 + parameters["number_of_wells_stimulated_0to1"] * parameters["number_of_wells"]), 
            # Constants
            OF=300
        ))

    def get_simplified_model(self):
        '''
        Compute constants (chi, gamma) and an expression for the simplified model
        :return:
        '''
        simplified_model_dict = {}

        for group in self.methods_groups:
            inf_params = group['parameters']
            par_dict_copy = deepcopy(self.par_subs_dict)
            [par_dict_copy.pop(self.correspondence_dict[p]) for p in inf_params]

            # chis, 20, 15, 10%
            if set(inf_params) == {'installed_capacity'}:
                P_ne = symbols('P_ne')
                for method in group['methods']:
                    is_dict = dict(self.i_coeff_matrix.T[method])
                    impact_copy = deepcopy(self.impact.subs(par_dict_copy))
                    impact_copy = impact_copy.subs(is_dict)
                    impact_copy = ratsimp(impact_copy)

                    chi1 = collect(impact_copy, 1/P_ne, evaluate=False)[1/P_ne]
                    chi2 = collect(impact_copy, 1/P_ne, evaluate=False)[1]
                    simplified_model_dict[method] = {
                        's_const': {1: chi1, 2: chi2},
                        's_model': lambda chi, parameters:
                        chi[1] / parameters['installed_capacity'] + chi[2]
                    }

            # chis, 5%
            if set(inf_params) == {'installed_capacity',
                                   'success_rate_primary_wells',
                                   'average_depth_of_wells'}:
                P_ne, SR_p, W_d = symbols('P_ne, SR_p, W_d')
                for method in group['methods']:
                    is_dict = dict(self.i_coeff_matrix.T[method])
                    impact_copy = deepcopy(self.impact.subs(par_dict_copy))
                    impact_copy = impact_copy.subs(is_dict)
                    impact_copy = ratsimp(impact_copy)

                    num = fraction(impact_copy.args[1])[0]
                    chi1 = collect(num, [SR_p * W_d, SR_p, W_d], evaluate=False)[SR_p * W_d]
                    chi2 = collect(num, [SR_p * W_d, SR_p, W_d], evaluate=False)[SR_p]
                    chi3 = collect(num, [SR_p * W_d, SR_p, W_d], evaluate=False)[W_d]
                    chi4 = impact_copy.args[0]

                    simplified_model_dict[method] = {
                        's_const': {1: chi1, 2: chi2, 3: chi3, 4: chi4},
                        's_model': lambda chi, parameters:
                        (parameters['success_rate_primary_wells'] * parameters['average_depth_of_wells'] * chi[1] \
                         + parameters['success_rate_primary_wells'] * chi[2] \
                         + parameters['average_depth_of_wells'] * chi[3]) \
                         / (parameters['success_rate_primary_wells'] * parameters['installed_capacity'])
                         + chi[4]
                    }

            # deltas 15/10%
            if set(inf_params) == {'installed_capacity',
                                   'specific_diesel_consumption'}:
                P_ne, D = symbols('P_ne, D')
                for method in group['methods']:
                    is_dict = dict(self.i_coeff_matrix.T[method])
                    impact_copy = deepcopy(self.impact.subs(par_dict_copy))
                    impact_copy = impact_copy.subs(is_dict)
                    impact_copy = ratsimp(impact_copy)

                    num = fraction(impact_copy.args[1])[0]
                    delta1 = collect(num, [D], evaluate=False)[D]
                    delta2 = collect(num, [D], evaluate=False)[1]
                    delta3 = impact_copy.args[0]

                    simplified_model_dict[method] = {
                        's_const': {1: delta1, 2: delta2, 3: delta3},
                        's_model': lambda delta, parameters:
                        (parameters['specific_diesel_consumption'] * delta[1] + delta[2]) \
                        / parameters['installed_capacity'] + delta[3]
                    }

            # deltas 5%
            if set(inf_params) == {'installed_capacity',
                                   'success_rate_primary_wells',
                                   'average_depth_of_wells',
                                   'specific_diesel_consumption'}:
                P_ne, SR_p, W_d, D = symbols('P_ne, SR_p, W_d, D')
                for method in group['methods']:
                    is_dict = dict(self.i_coeff_matrix.T[method])
                    impact_copy = deepcopy(self.impact.subs(par_dict_copy))
                    impact_copy = impact_copy.subs(is_dict)
                    impact_copy = ratsimp(impact_copy)

                    num = fraction(impact_copy.args[1])[0]
                    delta1 = collect(num, [D * SR_p * W_d, D * W_d, SR_p * W_d, SR_p, W_d], evaluate=False)[
                        D * SR_p * W_d]
                    delta2 = collect(num, [D * SR_p * W_d, D * W_d, SR_p * W_d, SR_p, W_d], evaluate=False)[D * W_d]
                    delta3 = collect(num, [D * SR_p * W_d, D * W_d, SR_p * W_d, SR_p, W_d], evaluate=False)[SR_p * W_d]
                    delta4 = collect(num, [D * SR_p * W_d, D * W_d, SR_p * W_d, SR_p, W_d], evaluate=False)[SR_p]
                    delta5 = collect(num, [D * SR_p * W_d, D * W_d, SR_p * W_d, SR_p, W_d], evaluate=False)[W_d]
                    delta6 = impact_copy.args[0]

                    simplified_model_dict[method] = {
                        's_const': {1: delta1, 2: delta2, 3: delta3, 4: delta4, 5: delta5, \
                                    6: delta6},
                        's_model': lambda delta, parameters:
                        (parameters['specific_diesel_consumption'] * parameters['success_rate_primary_wells']
                         * parameters['average_depth_of_wells'] * delta[1]
                         + parameters['specific_diesel_consumption'] * parameters['average_depth_of_wells'] * delta[2]
                         + parameters['success_rate_primary_wells'] * parameters['average_depth_of_wells'] * delta[3]
                         + parameters['success_rate_primary_wells'] * delta[4]
                         + parameters['average_depth_of_wells'] * delta[5])
                         / (parameters['success_rate_primary_wells'] * parameters['installed_capacity'])
                         + delta[6]
                    }

        return simplified_model_dict

    def run(self, parameters, lcia_methods=None):
        return super().run(parameters, self.simplified_model_dict, lcia_methods)

    def get_coeff(self, lcia_methods=None):
        return super().get_coeff(self.simplified_model_dict, lcia_methods)

#####################
### How to use it ###
#####################

# threshold = 0.05   # 20%
# s_ege = EnhancedSimplifiedModel(threshold)
# from ege_klausen import parameters
# n_iter = 400
# parameters.stochastic(n_iter)
# results = s_ege.run(parameters)
# results