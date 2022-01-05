# %% SETUP

import bw2data as bd
import pandas as pd
import warnings
from pathlib import Path

# Local files
from gsa_geothermal.utils import lookup_geothermal, get_EF_methods
from setups import setup_geothermal_gsa
from gsa_geothermal.parameters import get_parameters
from gsa_geothermal.simplified_models import ConventionalSimplifiedModel, EnhancedSimplifiedModel

if __name__ == '__main__':
    # Set project
    bd.projects.set_current("Geothermal")

    # Find demand
    _, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_conv_prod, electricity_enh_prod = lookup_geothermal()

    # Get methods
    methods = get_EF_methods()

    # Number of iterations
    iterations = 1000

    # Seed for stochastic parameters # TODO this needs to be moved e.g. in utils
    seed = 13413203
    option = "conventional"
    
    # save data
    write_dir_validation = Path("write_files") / "validation"
    
    # load data
    iterations_gsa = 500
    path_scores = Path("write_files") / "{}.N{}".format(option, iterations_gsa) / "scores"

    # To ignore warnings from MC (Sparse Efficiency Warning)
    warnings.filterwarnings("ignore")

    # Get parameters and simplified model class
    parameters = get_parameters(option)
    parameters.stochastic(iterations=iterations, seed=seed)

    # if "conventional" in option:
    #     ModelClass = ConventionalSimplifiedModel
    #     # demand = {electricity_conv_prod: 1}
    # elif "enhanced" in option:
    #     ModelClass = EnhancedSimplifiedModel
    #     # demand = {electricity_enh_prod: 1}

    # %% Model calculations

    thresholds = [0.2, 0.15, 0.1, 0.05]
    for threshold in thresholds:
        filename = "{}.simplified.t{:02d}.all_categories.N{}.seed{}.json".format(
            option, int(threshold*100), iterations, seed
        )
        filepath = write_dir_validation / filename
        if filepath.exists():
            print("{} already exists".format(filename))
        else:
            if "conventional" in option:
                model = ConventionalSimplifiedModel(setup_geothermal_gsa, path_scores, threshold, ch4=True)
            elif "enhanced" in option:
                model = EnhancedSimplifiedModel(setup_geothermal_gsa, path_scores, threshold)
            # Compute
            simplified_scores = model.run(parameters)
            # Save
            df_simplified_scores = pd.DataFrame.from_dict(simplified_scores)
            print("Saving {}".format(filepath))
            df_simplified_scores.to_json(filepath, double_precision=15)
