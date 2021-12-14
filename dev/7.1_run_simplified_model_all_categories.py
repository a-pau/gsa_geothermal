# %% SETUP

import brightway2 as bw
import pandas as pd
import warnings
from pathlib import Path

# Local files
from gsa_geothermal.utils import lookup_geothermal, get_EF_methods
from setups import setup_geothermal_gsa
from gsa_geothermal.parameters import get_parameters
from gsa_geothermal.simplified_models import ConventionalSimplifiedModel
from gsa_geothermal.simplified_models import EnhancedSimplifiedModel

if __name__ == '__main__':
    # Set project
    bw.projects.set_current("Geothermal")

    # Find demand
    _, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_conv_prod, electricity_enh_prod = lookup_geothermal()

    # Get methods
    methods = get_EF_methods()

    # Number of iterations
    iterations = 10 # TODO Need to be recalculated

    # Seed for stochastic parameters #TODO this needs to be moved e.g. in utils
    seed = 13413203
    
    # save data
    write_dir_validation = Path("write_files") / "validation"
    
    # load data
    iterations_gsa= 500
    path_conventional = Path("write_files") / "conventional.N{}".format(iterations_gsa) / "scores"
    path_enhanced = Path("write_files") / "enhanced.N{}".format(iterations_gsa) / "scores"

    # To ignore warnings from MC (Sparse Efficiency Warning)
    warnings.filterwarnings("ignore")

    # Get parameters
    cge_parameters = get_parameters("conventional")
    ege_parameters = get_parameters("enhanced")

    #%% CONVENTIONAL model calculations

    threshold = [0.2, 0.15, 0.1, 0.05]

    cge_parameters.stochastic(iterations=iterations, seed=seed)

    for t in threshold:

        # Initialize class
        cge_model_s = ConventionalSimplifiedModel(
            setup_geothermal_gsa=setup_geothermal_gsa,
            path=path_conventional,
            threshold=t,
        )

        # Compute
        cge_s = cge_model_s.run(cge_parameters)

        # Save
        cge_s_df = pd.DataFrame.from_dict(cge_s)
        filename_cge_s = "conventional.simplified.all_categories.N{}.threshold{}.json".format(iterations, t)
        filepath_cge_s = write_dir_validation / filename_cge_s
        print("Saving {}".format(filepath_cge_s))
        cge_s_df.to_json(filepath_cge_s, double_precision=15)

    #%% ENHANCED model calculations

    threshold = [0.2, 0.15, 0.1, 0.05]

    ege_parameters.stochastic(iterations=iterations, seed=seed)

    for t in threshold:

        # Initialize class
        ege_model_s = EnhancedSimplifiedModel(
            setup_geothermal_gsa=setup_geothermal_gsa,
            path=path_enhanced,
            threshold=t,
        )

        # Compute
        ege_s = ege_model_s.run(ege_parameters)

        # Save
        ege_s_df = pd.DataFrame.from_dict(ege_s)
        filename_ege_s = "enhanced.simplified.all_categories.N{}.threshold{}.json".format(iterations, t)
        filepath_ege_s = write_dir_validation / filename_ege_s
        print("Saving {}".format(filepath_ege_s))
        ege_s_df.to_json(filepath_ege_s, double_precision=15)