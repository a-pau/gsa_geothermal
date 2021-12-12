# %% SETUP

import brightway2 as bw
import pandas as pd
import warnings
from pathlib import Path

from gsa_geothermal.utils import lookup_geothermal, get_EF_methods
from gsa_geothermal.global_sensitivity_analysis import run_monte_carlo
from setups import setup_geothermal
from gsa_geothermal.parameters import get_parameters
from gsa_geothermal.general_models import GeothermalConventionalModel, GeothermalEnhancedModel
from gsa_geothermal.simplified_models import ConventionalSimplifiedModel
from gsa_geothermal.simplified_models import EnhancedSimplifiedModel

if __name__ == '__main__':
    # Set project
    bw.projects.set_current("Geothermal")

    # Find demand
    _, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_conv_prod, electricity_enh_prod = lookup_geothermal()

    # Get methods
    ILCD = get_EF_methods()

    # Number of iterations
    iterations = 1000

    # Seed for stochastic parameters
    seed = 13413203

    write_dir_validation = Path("write_files") / "validation"
    write_dir_conventional = Path("write_files") / "conventional.N{}".format(iterations)
    write_dir_enhanced = Path("write_files") / "enhanced.N{}".format(iterations)

    # # Folder and file name for saving
    # ecoinvent_version = "ecoinvent_3.6"
    # absolute_path = os.path.abspath(path)
    # folder_OUT = os.path.join(absolute_path, "generated_files", ecoinvent_version, "validation")
    # file_name = "ReferenceVsSimplified_N" + str(n_iter)

    # To ignore warnings from MC (Sparse Efficiency Warning)
    warnings.filterwarnings("ignore")

    # Get parameters
    cge_parameters = get_parameters("conventional")
    ege_parameters = get_parameters("enhanced")

    # %% CONVENTIONAL model calculations - REFERENCE TODO this has already been computed

    # Generate stochastic values
    cge_parameters.stochastic(iterations=iterations, seed=seed)

    # Compute
    cge_model = GeothermalConventionalModel(cge_parameters)
    cge_parameters_sto = cge_model.run_with_presamples(cge_parameters)
    cge_ref = run_monte_carlo(cge_parameters_sto, {electricity_conv_prod: 1}, ILCD, iterations)

    # Save
    cge_ref_df = pd.DataFrame.from_dict(cge_ref)

    filename_cge_ref = "conventional.simplified_vs_general.N().json".format(iterations)
    filepath_cge_ref = write_dir_validation / filename_cge_ref
    print("Saving {}".format(filepath_cge_ref))
    cge_ref_df.to_json(filepath_cge_ref, double_precision=15)

    # %% ENHANCED model calculations - REFERENCE
    # Generate stochastic values
    ege_parameters.stochastic(iterations=iterations, seed=seed)

    # Compute
    ege_model = GeothermalEnhancedModel(ege_parameters)
    ege_parameters_sto = ege_model.run_with_presamples(ege_parameters)
    ege_ref = run_monte_carlo(ege_parameters_sto, {electricity_enh_prod: 1}, ILCD, iterations)

    # Save
    ege_ref_df = pd.DataFrame.from_dict(ege_ref)

    filename_ege_ref = "enhanced.simplified_vs_general.N().json".format(iterations)
    filepath_ege_ref = write_dir_validation / filename_ege_ref
    print("Saving {}".format(filepath_ege_ref))
    cge_ref_df.to_json(filepath_ege_ref, double_precision=15)

    # %%CONVENTIONAL model calculations - SIMPLIFIED

    threshold = [0.2, 0.15, 0.1, 0.05]

    cge_parameters.stochastic(iterations=iterations, seed=seed)

    for t in threshold:

        # Initialize class
        cge_model_s = ConventionalSimplifiedModel(
            setup_geothermal_gsa=setup_geothermal,
            path=write_dir_conventional,
            threshold=t,
        )

        # Compute
        cge_s = cge_model_s.run(cge_parameters)

        # Save
        cge_s_df = pd.DataFrame.from_dict(cge_s)
        filename_cge_s = "conventional.simplified_vs_general.N().threshold{}.json".format(iterations, t)
        filepath_cge_s = write_dir_validation / filename_cge_s
        print("Saving {}".format(filepath_cge_s))
        cge_s_df.to_json(filepath_cge_s, double_precision=15)

    # %%ENHANCED model calculations - SIMPLIFIED

    threshold = [0.2, 0.15, 0.1, 0.05]

    ege_parameters.stochastic(iterations=iterations, seed=seed)

    for t in threshold:

        # Initialize class
        ege_model_s = EnhancedSimplifiedModel(
            setup_geothermal_gsa=setup_geothermal,
            path=write_dir_enhanced,
            threshold=t,
        )

        # Compute
        ege_s = ege_model_s.run(ege_parameters)

        # Save
        ege_s_df = pd.DataFrame.from_dict(ege_s)
        filename_ege_s = "enhanced.simplified_vs_general.N().threshold{}.json".format(iterations, t)
        filepath_ege_s = write_dir_validation / filename_ege_s
        print("Saving {}".format(filepath_ege_s))
        ege_s_df.to_json(filepath_ege_s, double_precision=15)
