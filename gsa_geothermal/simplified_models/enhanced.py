import numpy as np
from copy import deepcopy
from sympy import symbols, collect, ratsimp, fraction

# Local
from .base import GeothermalSimplifiedModel


class EnhancedSimplifiedModel(GeothermalSimplifiedModel):
    """Enhanced simplified model CHILD class."""
    def __init__(self, setup_geothermal_gsa, path, threshold, exploration=True):
        super(EnhancedSimplifiedModel, self).__init__(
            setup_geothermal_gsa=setup_geothermal_gsa,
            path=path,
            threshold=threshold,
            exploration=exploration,
            option="enhanced",
        )
        self.i_coeff_matrix["i6"] = 0
        from ..parameters.enhanced import get_parameters_enhanced
        parameters = get_parameters_enhanced()
        parameters.static()  # TODO Remember to fix this
        self.par_subs_dict = self.get_par_dict(parameters)
        self.complete_par_dict(parameters)
        self.simplified_model_dict = self.get_simplified_model()

    def complete_par_dict(self, parameters):
        self.par_subs_dict.update(
            dict(
                # Wells
                W_Pn=parameters["number_of_wells"],
                # Stimulation
                S_w=parameters["water_stimulation"],
                S_el=parameters["specific_electricity_stimulation"] / 1000,
                SW_n=np.round(
                    0.5
                    + parameters["number_of_wells_stimulated_0to1"]
                    * parameters["number_of_wells"]
                ),
                # Constants
                OF=300,
            )
        )

    def get_simplified_model(self):
        """
        Compute constants (chi, gamma) and an expression for the simplified model
        :return:
        """
        simplified_model_dict = dict()

        for group in self.methods_groups:
            inf_params = group["parameters"]
            par_dict_copy = deepcopy(self.par_subs_dict)
            [par_dict_copy.pop(self.correspondence_dict[p]) for p in inf_params]

            # chis, 20, 15, 10%
            if set(inf_params) == {"installed_capacity"}:
                P_ne = symbols("P_ne")
                for method in group["methods"]:
                    is_dict = dict(self.i_coeff_matrix.T[method])
                    impact_copy = deepcopy(self.impact.subs(par_dict_copy))
                    impact_copy = impact_copy.subs(is_dict)
                    impact_copy = ratsimp(impact_copy)

                    chi1 = collect(impact_copy, 1 / P_ne, evaluate=False)[1 / P_ne]
                    chi2 = collect(impact_copy, 1 / P_ne, evaluate=False)[1]
                    simplified_model_dict[method] = {
                        "s_const": {1: chi1, 2: chi2},
                        "s_model": lambda chi, parameters:
                            chi[1] / parameters["installed_capacity"] + chi[2],
                    }

            # chis, 5%
            if set(inf_params) == {
                "installed_capacity",
                "success_rate_primary_wells",
                "average_depth_of_wells",
            }:
                P_ne, SR_p, W_d = symbols("P_ne, SR_p, W_d")
                for method in group["methods"]:
                    is_dict = dict(self.i_coeff_matrix.T[method])
                    impact_copy = deepcopy(self.impact.subs(par_dict_copy))
                    impact_copy = impact_copy.subs(is_dict)
                    impact_copy = ratsimp(impact_copy)

                    num = fraction(impact_copy.args[1])[0]
                    chi1 = collect(num, [SR_p * W_d, SR_p, W_d], evaluate=False)[
                        SR_p * W_d
                        ]
                    chi2 = collect(num, [SR_p * W_d, SR_p, W_d], evaluate=False)[SR_p]
                    chi3 = collect(num, [SR_p * W_d, SR_p, W_d], evaluate=False)[W_d]
                    chi4 = impact_copy.args[0]

                    simplified_model_dict[method] = {
                        "s_const": {1: chi1, 2: chi2, 3: chi3, 4: chi4},
                        "s_model": lambda chi, parameters: (
                               parameters["success_rate_primary_wells"]
                               * parameters["average_depth_of_wells"]
                               * chi[1]
                               + parameters["success_rate_primary_wells"] * chi[2]
                               + parameters["average_depth_of_wells"] * chi[3]
                        )
                        / (
                               parameters["success_rate_primary_wells"]
                               * parameters["installed_capacity"]
                        )
                        + chi[4],
                    }

            # deltas 15/10%
            if set(inf_params) == {"installed_capacity", "specific_diesel_consumption"}:
                P_ne, D = symbols("P_ne, D")
                for method in group["methods"]:
                    is_dict = dict(self.i_coeff_matrix.T[method])
                    impact_copy = deepcopy(self.impact.subs(par_dict_copy))
                    impact_copy = impact_copy.subs(is_dict)
                    impact_copy = ratsimp(impact_copy)

                    num = fraction(impact_copy.args[1])[0]
                    delta1 = collect(num, [D], evaluate=False)[D]
                    delta2 = collect(num, [D], evaluate=False)[1]
                    delta3 = impact_copy.args[0]

                    simplified_model_dict[method] = {
                        "s_const": {1: delta1, 2: delta2, 3: delta3},
                        "s_model": lambda delta, parameters: (
                             parameters["specific_diesel_consumption"] * delta[1]
                             + delta[2]
                        )
                        / parameters["installed_capacity"]
                        + delta[3],
                    }

            # deltas 5%
            if set(inf_params) == {
                "installed_capacity",
                "success_rate_primary_wells",
                "average_depth_of_wells",
                "specific_diesel_consumption",
            }:
                P_ne, SR_p, W_d, D = symbols("P_ne, SR_p, W_d, D")
                for method in group["methods"]:
                    is_dict = dict(self.i_coeff_matrix.T[method])
                    impact_copy = deepcopy(self.impact.subs(par_dict_copy))
                    impact_copy = impact_copy.subs(is_dict)
                    impact_copy = ratsimp(impact_copy)

                    num = fraction(impact_copy.args[1])[0]
                    delta1 = collect(
                        num,
                        [D * SR_p * W_d, D * W_d, SR_p * W_d, SR_p, W_d],
                        evaluate=False,
                    )[D * SR_p * W_d]
                    delta2 = collect(
                        num,
                        [D * SR_p * W_d, D * W_d, SR_p * W_d, SR_p, W_d],
                        evaluate=False,
                    )[D * W_d]
                    delta3 = collect(
                        num,
                        [D * SR_p * W_d, D * W_d, SR_p * W_d, SR_p, W_d],
                        evaluate=False,
                    )[SR_p * W_d]
                    delta4 = collect(
                        num,
                        [D * SR_p * W_d, D * W_d, SR_p * W_d, SR_p, W_d],
                        evaluate=False,
                    )[SR_p]
                    delta5 = collect(
                        num,
                        [D * SR_p * W_d, D * W_d, SR_p * W_d, SR_p, W_d],
                        evaluate=False,
                    )[W_d]
                    delta6 = impact_copy.args[0]

                    simplified_model_dict[method] = {
                        "s_const": {
                            1: delta1,
                            2: delta2,
                            3: delta3,
                            4: delta4,
                            5: delta5,
                            6: delta6,
                        },
                        "s_model": lambda delta, parameters: (
                             parameters["specific_diesel_consumption"]
                             * parameters["success_rate_primary_wells"]
                             * parameters["average_depth_of_wells"]
                             * delta[1]
                             + parameters["specific_diesel_consumption"]
                             * parameters["average_depth_of_wells"]
                             * delta[2]
                             + parameters["success_rate_primary_wells"]
                             * parameters["average_depth_of_wells"]
                             * delta[3]
                             + parameters["success_rate_primary_wells"] * delta[4]
                             + parameters["average_depth_of_wells"] * delta[5]
                        )
                        / (
                             parameters["success_rate_primary_wells"]
                             * parameters["installed_capacity"]
                        )
                        + delta[6],
                    }

        return simplified_model_dict

    def run(self, parameters, lcia_methods=None):
        return super().run(parameters, self.simplified_model_dict, lcia_methods)

    def get_coeff(self, lcia_methods=None):
        return super().get_coeff(self.simplified_model_dict, lcia_methods)
