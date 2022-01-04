#%% Set-up
import bw2data as bd
import pandas as pd
from pathlib import Path

# Import local
from gsa_geothermal.utils import get_EF_methods
from gsa_geothermal.simplified_models import ConventionalSimplifiedModel, EnhancedSimplifiedModel
from setups import setup_geothermal_gsa

# Set project
bd.projects.set_current("Geothermal")

# Retrieve methods
methods, methods_units = get_EF_methods(return_units=True)

# Save data path
write_dir_validation = Path("write_files") / "validation"

# Path to MC scores
iterations_gsa = 500
path_scores_conv = Path("write_files") / "conventional.N{}".format(iterations_gsa) / "scores"
path_scores_enh = Path("write_files") / "enhanced.N{}".format(iterations_gsa) / "scores"

# Simplified models thresholds
thresholds = [0.2, 0.15, 0.1, 0.05]

# Klausen parameter values

# Hellisheidi
cge_parameters = {
    "co2_emissions": 20.9 / 1000,
    "gross_power_per_well": 9,
    "average_depth_of_wells": 2220,
    "initial_harmonic_decline_rate": 0.03,
    "success_rate_primary_wells": 100,
}

# UDDGP
ege_parameters = {
    "installed_capacity": 1,
    "average_depth_of_wells": 4000,
    "specific_diesel_consumption": 7.2 * 1000,
    "success_rate_primary_wells": 100,
}

#%% CONVENTIONAL model calculations

# Initialize classes
cge_model_s = {}
for t in thresholds:
    cge_model_s[t] = ConventionalSimplifiedModel(
        setup_geothermal_gsa=setup_geothermal_gsa,
        path=path_scores_conv,
        threshold=t)
    
cge_s = {}   
for t in thresholds:
    cge_s[t] = cge_model_s[t].run(cge_parameters, lcia_methods=methods)

# Re-arrange results
cge_s_df = pd.DataFrame.from_dict(cge_s)
cge_s_df.columns = ["{:.0%}".format(t) for t in cge_s_df.columns]
cge_s_df = cge_s_df.reset_index().rename(columns={"index": "method"})

# Save
filename_cge_s = "simplified_model.hellisheidi.json"
filepath_cge_s = write_dir_validation / filename_cge_s
print("Saving {}".format(filepath_cge_s))
cge_s_df.to_json(filepath_cge_s)
    
#%% ENHANCED model calculations

for exploration in [True, False]:
    
    # Initialize class 
    ege_model_s = {}
    for t in thresholds:
        ege_model_s[t] = EnhancedSimplifiedModel(
            setup_geothermal_gsa=setup_geothermal_gsa,
            path=path_scores_enh,
            threshold=t,
            exploration=exploration
        )
    
    # Compute
    ege_s = {}
    for t in thresholds:
        ege_s[t] = ege_model_s[t].run(ege_parameters, lcia_methods=methods)
    
    # Re-arrange results
    ege_s_df = pd.DataFrame.from_dict(ege_s)
    ege_s_df.columns = ["{:.0%}".format(t) for t in ege_s_df.columns]
    ege_s_df = ege_s_df.reset_index().rename(columns={"index": "method"})
    
    # Save
    filename_ege_s = "simplified_model.uddgp.exploration_{}.json".format(exploration)
    filepath_ege_s = write_dir_validation / filename_ege_s
    print("Saving {}".format(filepath_ege_s))
    ege_s_df.to_json(filepath_ege_s)
