# %% SETUP

import brightway2 as bw
import pandas as pd
import warnings
from pathlib import Path

# Local files
from gsa_geothermal.utils import lookup_geothermal, get_EF_methods
from gsa_geothermal.global_sensitivity_analysis import run_monte_carlo
from gsa_geothermal.parameters import get_parameters
from gsa_geothermal.general_models import GeothermalConventionalModel, GeothermalEnhancedModel

if __name__ == '__main__':
    # Set project
    bw.projects.set_current("Geothermal")

    # Find demand
    _, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_conv_prod, electricity_enh_prod = lookup_geothermal()

    # Get methods
    methods = get_EF_methods()

    # Number of iterations # TODO to be recalculated 
    iterations = 10

    # Seed for stochastic parameters #TODO this needs to be moved e.g. in utils
    seed = 13413203

    #save data
    write_dir_validation = Path("write_files") / "validation"
    write_dir_validation.mkdir(parents=True, exist_ok=True)

    # To ignore warnings from MC (Sparse Efficiency Warning)
    warnings.filterwarnings("ignore")

    # Get parameters
    cge_parameters = get_parameters("conventional")
    ege_parameters = get_parameters("enhanced")

    # %% CONVENTIONAL model calculations

    # Generate stochastic values
    cge_parameters.stochastic(iterations=iterations, seed=seed)

    # Compute
    cge_model = GeothermalConventionalModel(cge_parameters)
    cge_parameters_sto = cge_model.run_with_presamples(cge_parameters)
    cge_ref = run_monte_carlo(cge_parameters_sto, {electricity_conv_prod: 1}, methods, iterations)

    # Save
    cge_ref_df = pd.DataFrame.from_dict(cge_ref)

    filename_cge_ref = "conventional.general.all_categories.N{}.json".format(iterations)
    filepath_cge_ref = write_dir_validation / filename_cge_ref
    print("Saving {}".format(filepath_cge_ref))
    cge_ref_df.to_json(filepath_cge_ref, double_precision=15)

    # %% ENHANCED model calculations
    # Generate stochastic values
    ege_parameters.stochastic(iterations=iterations, seed=seed)

    # Compute
    ege_model = GeothermalEnhancedModel(ege_parameters)
    ege_parameters_sto = ege_model.run_with_presamples(ege_parameters)
    ege_ref = run_monte_carlo(ege_parameters_sto, {electricity_enh_prod: 1}, methods, iterations)

    # Save
    ege_ref_df = pd.DataFrame.from_dict(ege_ref)

    filename_ege_ref = "enhanced.general.all_categories.N{}.json".format(iterations)
    filepath_ege_ref = write_dir_validation / filename_ege_ref
    print("Saving {}".format(filepath_ege_ref))
    ege_ref_df.to_json(filepath_ege_ref, double_precision=15)
