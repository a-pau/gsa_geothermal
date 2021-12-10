import bw2data as bd
from copy import deepcopy
from sympy import symbols, collect, ratsimp

# Local
from ..utils import get_EF_methods
from .base import GeothermalSimplifiedModel


class ConventionalSimplifiedModel(GeothermalSimplifiedModel):
    """Conventional simplified model CHILD class"""
    def __init__(self, setup_geothermal_gsa, path, threshold, exploration=True):
        super(ConventionalSimplifiedModel, self).__init__(
            setup_geothermal_gsa=setup_geothermal_gsa,
            path=path,
            threshold=threshold,
            exploration=exploration,
            option="conventional",
        )
        self.i_coeff_matrix["i5_1"] = 0
        self.i_coeff_matrix["i5_2"] = 0
        from ..parameters.conventional import get_parameters_conventional
        parameters = get_parameters_conventional()
        parameters.static()
        self.par_subs_dict = self.get_par_dict(parameters)
        self.complete_par_dict(parameters)
        self.ch4_CF = self.get_ch4_cf()
        self.simplified_model_dict = self.get_simplified_model()

    @staticmethod
    def get_ch4_cf():
        db_biosph = bd.Database("biosphere3")
        ch4 = [
            act
            for act in db_biosph
            if "Methane, fossil" == act["name"]
            and "air" in act["categories"]
            and "low" not in str(act["categories"])
            and "urban" not in str(act["categories"])
        ][0].key
        ILCD_CC = get_EF_methods(select_climate_change_only=True)[0]
        ch4_CF = [cf[1] for cf in bd.Method(ILCD_CC).load() if cf[0] == ch4][0]
        return ch4_CF

    def complete_par_dict(self, parameters):
        """
        Add values to a substitution dictionary that are CGE specific
        :param parameters:
        :return:
        """
        self.par_subs_dict.update(
            dict(
                # Wells
                CW_ne=parameters["gross_power_per_well"],
                D_i=parameters["initial_harmonic_decline_rate"],
                PIratio=parameters["production_to_injection_ratio"],
                # Success rate
                SR_m=parameters["success_rate_makeup_wells"],
                # Operational CO2 emissions
                E_co2=parameters["co2_emissions"],
                # Constants
                OF=0,
            )
        )

    def get_simplified_model(self):
        """
        Compute constants (alpha, beta) and an expression for the simplified model
        :return:
        """
        simplified_model_dict = dict()

        for group in self.methods_groups:
            inf_params = group["parameters"]
            par_dict_copy = deepcopy(self.par_subs_dict)
            [par_dict_copy.pop(self.correspondence_dict[p]) for p in inf_params]

            # Alphas all thresholds
            if set(inf_params) == {"co2_emissions"}:
                E_co2 = symbols("E_co2")
                impact_copy = deepcopy(self.impact.subs(par_dict_copy))
                alpha1 = collect(impact_copy, E_co2, evaluate=False)[E_co2]
                alpha2 = collect(impact_copy, E_co2, evaluate=False)[1]
                for method in group["methods"]:
                    is_dict = dict(self.i_coeff_matrix.T[method])
                    alpha1_val = alpha1.subs(is_dict)
                    alpha2_val = alpha2.subs(is_dict)
                    simplified_model_dict[method] = {
                        "s_const": {1: alpha1_val, 2: alpha2_val},
                        "s_model": lambda alpha, parameters: parameters["co2_emissions"]
                        * alpha[1]
                        + alpha[2],
                        "s_model_ch4": lambda alpha, parameters: parameters[
                            "co2_emissions"
                        ]
                        * alpha[1]
                        + alpha[2]
                        + self.ch4_CF * parameters["ch4_emissions"],
                    }

            # Betas, 20/15%
            elif set(inf_params) == {"gross_power_per_well", "average_depth_of_wells"}:
                W_d, CW_ne = symbols("W_d, CW_ne")
                for method in group["methods"]:
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
                        "s_const": {1: beta1, 2: beta2, 3: beta3, 4: beta4},
                        "s_model": lambda beta, parameters: (
                            parameters["average_depth_of_wells"] * beta[1] + beta[2]
                        )
                        / parameters["gross_power_per_well"]
                        + parameters["average_depth_of_wells"] * beta[3]
                        + beta[4],
                    }

            # Betas, 10%
            elif set(inf_params) == {
                "gross_power_per_well",
                "average_depth_of_wells",
                "initial_harmonic_decline_rate",
            }:
                W_d, CW_ne, D_i = symbols("W_d, CW_ne, D_i")
                for method in group["methods"]:
                    is_dict = dict(self.i_coeff_matrix.T[method])
                    impact_copy = deepcopy(self.impact.subs(par_dict_copy))
                    impact_copy = impact_copy.subs(is_dict)
                    impact_copy = ratsimp(impact_copy)
                    temp = collect(impact_copy, [1 / CW_ne, 1, W_d], evaluate=False)
                    temp2 = collect(
                        temp[1 / CW_ne], [D_i * W_d, D_i, W_d, 1], evaluate=False
                    )
                    beta1 = temp2[D_i * W_d]
                    beta2 = temp2[D_i]
                    beta3 = temp2[W_d]
                    beta4 = temp2[1]
                    beta5 = temp[W_d]
                    beta6 = temp[1]
                    simplified_model_dict[method] = {
                        "s_const": {
                            1: beta1,
                            2: beta2,
                            3: beta3,
                            4: beta4,
                            5: beta5,
                            6: beta6,
                        },
                        "s_model": lambda beta, parameters: (
                            parameters["initial_harmonic_decline_rate"]
                            * parameters["average_depth_of_wells"]
                            * beta[1]
                            + parameters["initial_harmonic_decline_rate"] * beta[2]
                            + parameters["average_depth_of_wells"] * beta[3]
                            + beta[4]
                        )
                        / parameters["gross_power_per_well"]
                        + parameters["average_depth_of_wells"] * beta[5]
                        + beta[6],
                    }

            # Betas, 5%
            elif set(inf_params) == {
                "gross_power_per_well",
                "average_depth_of_wells",
                "initial_harmonic_decline_rate",
                "success_rate_primary_wells",
            }:
                W_d, CW_ne, D_i, SR_p = symbols("W_d, CW_ne, D_i, SR_p")
                for method in group["methods"]:
                    is_dict = dict(self.i_coeff_matrix.T[method])
                    impact_copy = deepcopy(self.impact.subs(par_dict_copy))
                    impact_copy = impact_copy.subs(is_dict)
                    impact_copy = ratsimp(impact_copy)
                    temp = collect(impact_copy, [CW_ne*SR_p], evaluate=False)
                    temp2 = collect(
                        temp[list(temp.keys())[0]],
                        [SR_p * W_d * D_i, D_i * SR_p, SR_p, W_d],
                        evaluate=False,
                    )
                    beta1 = temp2[SR_p * D_i * W_d]
                    beta2 = temp2[D_i * SR_p]
                    beta3 = temp2[W_d]
                    beta4 = temp2[SR_p]
                    beta5 = collect(temp[1], [W_d, 1], evaluate=False)[W_d]
                    beta6 = collect(temp[1], [W_d, 1], evaluate=False)[1]
                    simplified_model_dict[method] = {
                        "s_const": {
                            1: beta1,
                            2: beta2,
                            3: beta3,
                            4: beta4,
                            5: beta5,
                            6: beta6,
                        },
                        "s_model": lambda beta, parameters: parameters[
                            "initial_harmonic_decline_rate"
                        ]
                        * (parameters["average_depth_of_wells"] * beta[1] + beta[2])
                        / parameters["gross_power_per_well"]
                        + (
                            parameters["average_depth_of_wells"] * beta[3]
                            + parameters["success_rate_primary_wells"] * beta[4]
                        )
                        / parameters["gross_power_per_well"]
                        / parameters["success_rate_primary_wells"]
                        + parameters["average_depth_of_wells"] * beta[5]
                        + beta[6],
                    }

        return simplified_model_dict

    def run(self, parameters, lcia_methods=None, ch4=False):
        return super().run(parameters, self.simplified_model_dict, lcia_methods, ch4)

    def get_coeff(self, lcia_methods=None):
        return super().get_coeff(self.simplified_model_dict, lcia_methods)
