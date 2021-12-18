import brightway2 as bw
import pandas as pd
from pathlib import Path
from time import time

# Local files
from gsa_geothermal.utils import lookup_geothermal, get_EF_methods
from gsa_geothermal.general_models import GeothermalConventionalModel, GeothermalEnhancedModel
from gsa_geothermal.parameters import get_parameters
from gsa_geothermal.global_sensitivity_analysis import run_monte_carlo

if __name__ == '__main__':
    # Set project
    bw.projects.set_current("Geothermal")
    select_climate_change_only = False
    if select_climate_change_only:
        methods_str = "climate_change"
    else:
        methods_str = "all_categories"

    # Method
    methods = get_EF_methods(select_climate_change_only=select_climate_change_only)

    # Find demand
    _, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_conv_prod, electricity_enh_prod = lookup_geothermal()

    # Number of iterations
    iterations = 10000
    
    # Seed for stochastic parameters  # TODO this needs to be moved e.g. in utils
    seed = 13413203

    # Options
    option = "conventional"
    exploration = True
    success_rate = True

    # Save data
    write_dir = Path("write_files") / "validation"
    write_dir.mkdir(parents=True, exist_ok=True)
    filename = "{}.general.{}.N{}.seed{}.json".format(option, methods_str, iterations, seed)
    filepath = write_dir / filename

    if filepath.exists():
        print("{} already exists".format(filename))
    else:
        # Run general model
        parameters = get_parameters(option)
        parameters.stochastic(iterations=iterations, seed=seed)
        if "conventional" in option:
            ModelClass = GeothermalConventionalModel
            demand = {electricity_conv_prod: 1}
        elif "enhanced" in option:
            ModelClass = GeothermalEnhancedModel
            demand = {electricity_enh_prod: 1}
        model = ModelClass(parameters, exploration, success_rate)

        parameters = model.run_with_presamples(parameters)
        t0 = time()
        general_scores = run_monte_carlo(parameters, demand, methods, iterations)
        print("Monte Carlo took {:6.2f} seconds".format(time()-t0))

        df_general_scores = pd.DataFrame.from_dict(general_scores, orient="columns")

        if select_climate_change_only:
            df_general_scores.columns = ["carbon footprint"]
            # Multiply by 1000 to get gCO2 eq.
            df_general_scores["carbon footprint"] = df_general_scores["carbon footprint"] * 1000

        print("Saving {}".format(filepath))
        df_general_scores.to_json(filepath)
