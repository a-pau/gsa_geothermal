import bw2data as bd
import bw2calc as bc
import numpy as np
import pandas as pd
from sympy import symbols

# Local
from ..utils import lookup_geothermal, get_lcia_results, get_EF_methods
from ..global_sensitivity_analysis import my_sobol_analyze


class GeothermalSimplifiedModel:
    """Geothermal simplified model PARENT class."""
    def __init__(self, setup_geothermal_gsa, path, threshold, exploration, option):
        self.option = option
        self.threshold = threshold
        total_df = self.get_total_indices(setup_geothermal_gsa, path)
        self.total_df = total_df
        self.methods = get_EF_methods()
        self.methods_groups = self.get_methods_groups(total_df, self.threshold)
        self.i_coeff_matrix = self.compute_i_coeff()
        self.impact = self.define_symbolic_eq()
        self.exploration = exploration

        self.correspondence_dict = {
            "co2_emissions": "E_co2",
            "gross_power_per_well": "CW_ne",
            "average_depth_of_wells": "W_d",
            "initial_harmonic_decline_rate": "D_i",
            "success_rate_primary_wells": "SR_p",
            "installed_capacity": "P_ne",
            "specific_diesel_consumption": "D",
        }

    def get_total_indices(self, setup_geothermal_gsa, path):
        problem, calc_second_order, parameters_list, methods = setup_geothermal_gsa(self.option)

        scores = get_lcia_results(path)
        sa_dict = dict(parameters=parameters_list)
        for i, method in enumerate(methods):
            method_name = method[-2]
            Y = scores[:, i]
            sa_dict[method_name] = my_sobol_analyze(problem, Y, calc_second_order)

        # Extract total index into a dictionary and dataframe
        total_dict = dict()
        total_dict["parameters"] = parameters_list
        total_dict.update({k: v["ST"] for k, v in sa_dict.items() if k != "parameters"})
        total_df = pd.DataFrame(total_dict)
        total_df = total_df.set_index("parameters")
        return total_df

    @staticmethod
    def get_methods_groups(total_df, threshold):
        """Get methods groups for only one threshold."""
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

            methods_groups.append(
                {
                    "parameters": list(df_use_params.index.values[np.where(u != 0)[0]]),
                    "methods": list_,
                }
            )

        return methods_groups

    def compute_i_coeff(self):
        # Retrieve activities
        (
            wellhead,
            diesel,
            steel,
            cement,
            water,
            drilling_mud,
            drill_wst,
            wells_closr,
            coll_pipe,
            plant,
            ORC_fluid,
            ORC_fluid_wst,
            diesel_stim,
            co2,
            _,
            _,
        ) = lookup_geothermal()
        cooling_tower = bd.Database("geothermal energy").search("cooling tower")[0].key

        list_act = [
            wellhead,
            diesel,
            steel,
            cement,
            water,
            drilling_mud,
            drill_wst,
            wells_closr,
            coll_pipe,
            plant,
            cooling_tower,
            ORC_fluid,
            ORC_fluid_wst,
            diesel_stim,
        ]

        # Calculate impact of activities
        lca = bc.LCA({list_act[0]: 1}, self.methods[0])
        lca.lci()
        lca.lcia()
        coeff = dict()
        for method in self.methods:
            s = []
            lca.switch_method(method)
            for act in list_act:
                lca.redo_lcia({act: 1})
                s.append(lca.score)
            coeff[method[-2]] = s

        # Retrieve CF for co2 emissions
        for method in self.methods:
            CFs = bd.Method(method).load()
            coeff[method[-2]].append(next((cf[1] for cf in CFs if cf[0] == co2), 0))

        # Build matrix
        col_names = [
            "wellhead",
            "diesel",
            "steel",
            "cement",
            "water",
            "drilling_mud",
            "drill_wst",
            "wells_closr",
            "coll_pipe",
            "plant",
            "cooling tower",
            "ORC_fluid",
            "ORC_fluid_wst",
            "diesel_stim",
            "co2",
        ]
        i_coeff_matrix = pd.DataFrame.from_dict(
            coeff, orient="index", columns=col_names
        )

        # Re-arrange matrix
        i_coeff_matrix["concrete"] = (
                i_coeff_matrix["cement"] + i_coeff_matrix["water"] * 1 / 0.65
        )
        i_coeff_matrix["ORC_fluid_tot"] = (
                i_coeff_matrix["ORC_fluid"] - i_coeff_matrix["ORC_fluid_wst"]
        )
        i_coeff_matrix["electricity_stim"] = i_coeff_matrix["diesel_stim"] * 3.6
        i_coeff_matrix["drill_wst"] = i_coeff_matrix["drill_wst"] * -1
        i_coeff_matrix = i_coeff_matrix.drop(
            columns=["cement", "ORC_fluid", "ORC_fluid_wst", "diesel_stim"]
        )

        col_ord = [
            "wellhead",
            "diesel",
            "steel",
            "concrete",
            "drilling_mud",
            "drill_wst",
            "wells_closr",
            "coll_pipe",
            "plant",
            "cooling tower",
            "ORC_fluid_tot",
            "water",
            "electricity_stim",
            "co2",
        ]
        i_coeff_matrix = i_coeff_matrix[col_ord]

        is_ = [
            "i1",
            "i2_1",
            "i2_2",
            "i2_3",
            "i2_4",
            "i2_5",
            "i2_6",
            "i3",
            "i4_1",
            "i4_2",
            "i4_3",
            "i5_1",
            "i5_2",
            "i6",
        ]

        if len(i_coeff_matrix.columns) == len(is_):
            i_coeff_matrix.columns = is_

        return i_coeff_matrix

    def define_symbolic_eq(self):
        # 1. Main parameters as in Table 1 of the paper
        # Power plant
        P_ne, AP, CF, LT, CP, E_co2 = symbols("P_ne, AP, CF, LT, CP, E_co2")
        # Wells
        CW_ne, W_d, D, Cs, Cc, DM, D_i, PIratio = symbols(
            "CW_ne, W_d, D, Cs, Cc, DM, D_i, PIratio"
        )
        # Success rate
        SR_e, SR_p, SR_m = symbols("SR_e, SR_p, SR_m")
        # Stimulation
        S_w, S_el, SW_n = symbols("S_w, S_el, SW_n")
        # 2. Fixed parameters as in Table 2 of the paper
        W_en, OF, CT_n, DW = symbols("W_en, OF, CT_n, DW")
        # 3. `i` Coefficients
        (
            i1,
            i2_1,
            i2_2,
            i2_3,
            i2_4,
            i2_5,
            i2_6,
            i3,
            i4_1,
            i4_2,
            i4_3,
            i5_1,
            i5_2,
            i6,
        ) = symbols(
            "i1, i2_1, i2_2, i2_3, i2_4, i2_5, i2_6, i3, i4_1, i4_2, i4_3, i5_1, i5_2, i6"
        )

        # Total number of wells with success rate
        if self.option == "conventional":
            W_Pn = P_ne / CW_ne  # production wells
            W_n_sr = W_Pn * ((1 + 1 / PIratio) / (SR_p / 100) + D_i * LT / (SR_m / 100))
            W_n = W_Pn * ((1 + 1 / PIratio) + D_i * LT)
        elif self.option == "enhanced":
            W_Pn = symbols("W_Pn")
            W_n_sr = W_Pn / (SR_p / 100)
            W_n = W_Pn

        W_E_en_sr = W_en * 0.3 / (SR_e / 100)
        W_E_en = W_en * 0.3

        # Impacts of each component from Equation 1
        wells = (W_n + W_E_en) * i1 + (W_n_sr + W_E_en_sr) * W_d * (
                D * i2_1 + Cs * i2_2 + Cc * i2_3 + DM * i2_4 + DW * i2_5 + i2_6
        )
        collection_pipelines = W_n * CP * i3
        power_plant = P_ne * (i4_1 + CT_n * i4_2 + OF * i4_3)
        stimulation = (
                SW_n * S_w * (i5_1 + S_el * i5_2)
        )  # NO W_n here, because it is included in SW_n
        operational_emissions = E_co2 * i6
        lifetime = P_ne * CF * (1 - AP) * LT * 8760 * 1000

        # Main equation
        impact = (
                         wells + collection_pipelines + power_plant + stimulation
                 ) / lifetime + operational_emissions

        return impact

    def get_par_dict(self, parameters):
        """
        Substitution dictionary for symbolic subs
        :param parameters:
        :return:
        """
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

        if self.exploration:
            par_dict.update(dict(W_en=3))
        else:
            # Note, W_en can't be zero because chi 5% equations won't work.
            par_dict.update(dict(W_en=0.00001))

        return par_dict

    def run(self, parameters_sto, simplified_model_dict, lcia_methods=None, ch4=False):
        """Run simplified model."""
        if lcia_methods is None:
            lcia_methods = self.methods

        results = dict()
        for method in lcia_methods:
            s_const = simplified_model_dict[method[-2]]["s_const"]
            if ch4 and method[-2] == "climate change no LT":
                s_model = simplified_model_dict[method[-2]]["s_model_ch4"]
            else:
                s_model = simplified_model_dict[method[-2]]["s_model"]

            res = s_model(s_const, parameters_sto)

            if isinstance(res, np.ndarray):
                res = res.astype("float")
            else:
                res = float(res)

            results[method[-2]] = res

        return results

    def get_coeff(self, simplified_model_dict, lcia_methods=None):

        if lcia_methods is None:
            lcia_methods = self.methods

        coeff = dict()
        for method in lcia_methods:
            coeff[method[-2]] = simplified_model_dict[method[-2]]["s_const"]

        return coeff
