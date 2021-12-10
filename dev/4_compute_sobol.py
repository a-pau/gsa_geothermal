import pandas as pd
from pathlib import Path

# Local files
from setups import setup_geothermal_gsa
from gsa_geothermal.utils import get_lcia_results
from gsa_geothermal.global_sensitivity_analysis import my_sobol_analyze
from gsa_geothermal.plotting.utils import save_dict_json, methods_dict


if __name__ == "__main__":

    option = "conventional.diff_distributions"
    iterations = 500

    # Load data and setup everything
    path_base = Path("write_files") / "{}.N{}".format(option, iterations)
    path_scores = path_base / "scores"
    scores = get_lcia_results(path_scores)
    problem, calc_second_order, parameters_list, methods = setup_geothermal_gsa(option)

    sa_dict = dict(parameters=parameters_list)
    for i, method in enumerate(methods):
        method_name = method[-2]
        Y = scores[:, i]
        sa_dict[method_name] = my_sobol_analyze(problem, Y, calc_second_order)

    parameters = sa_dict["parameters"]
    n_parameters = len(parameters)

    # Extract total index into a dictionary and dataframe
    total_dict, first_dict = {}, {}
    total_dict["parameters"] = parameters
    first_dict["parameters"] = parameters
    for k in sa_dict.keys():
        new_key = methods_dict.get(k, k)
        if k != "parameters":
            total_dict[new_key] = sa_dict[k]["ST"]
            first_dict[new_key] = [
                abs(a) for a in sa_dict[k]["S1"]
            ]  # [abs(a) for a in all_vals_first[n_all-n_parameters:]]
    total_df = pd.DataFrame(total_dict)
    first_df = pd.DataFrame(first_dict)

    # Save GSA results
    first_df.to_excel(path_base / "sobol_first.xlsx", index=False)
    total_df.to_excel(path_base / "sobol_total.xlsx", index=False)
    sa_dict_save = save_dict_json(sa_dict, path_base / "sobol_indices.json")
