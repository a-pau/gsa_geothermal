# %% Set-up
import bw2data as bd
import pandas as pd
from pathlib import Path

# Import local
from gsa_geothermal.utils import get_EF_methods
from gsa_geothermal.data import (
    get_df_carbon_footprints_from_literature_conventional,
    get_df_carbon_footprints_from_literature_enhanced
)
from gsa_geothermal.simplified_models import ConventionalSimplifiedModel, EnhancedSimplifiedModel
from setups import setup_geothermal_gsa

if __name__ == '__main__':
    # Set project
    bd.projects.set_current("Geothermal")

    # Method
    method = get_EF_methods(select_climate_change_only=True)
    
    # Save data path
    write_dir_validation = Path("write_files") / "validation"

    # Path to MC scores
    iterations_gsa = 500
    path_scores_conv = Path("write_files") / "conventional.N{}".format(iterations_gsa) / "scores"
    path_scores_enh = Path("write_files") / "enhanced.N{}".format(iterations_gsa) / "scores"

    # Load literature data
    df_conventional_literature = get_df_carbon_footprints_from_literature_conventional()
    df_enhanced_literature = get_df_carbon_footprints_from_literature_enhanced()
    df_conventional_literature = df_conventional_literature.dropna(
        subset=["Operational CO2 emissions (g/kWh)"]
    ).reset_index(
        drop=True
    )
    df_enhanced_literature = df_enhanced_literature.dropna(
        subset=[
            'Diesel consumption (GJ/m)',
            'Installed capacity (MW)',
            'Depth of wells (m)',
            'Success rate (%)'
        ]
    ).reset_index(
        drop=True
    )
        
    df_conventional_literature = df_conventional_literature[df_conventional_literature.columns[[0,3,4]]]
    df_conventional_literature.columns = ["study", "co2_emissions", "ch4_emissions"]
    df_conventional_literature["co2_emissions"] = df_conventional_literature["co2_emissions"] / 1000
    df_conventional_literature["ch4_emissions"] = df_conventional_literature["ch4_emissions"] / 1000
    df_conventional_literature = df_conventional_literature.sort_values(by="study")

    df_enhanced_literature = df_enhanced_literature[df_enhanced_literature.columns[[0, 2, 3, 4, 5, 6]]]
    df_enhanced_literature.columns = [
        "study",
        "carbon footprint",
        "specific_diesel_consumption",
        "installed_capacity",
        "average_depth_of_wells",
        "success_rate_primary_wells",
    ]
    
    df_enhanced_literature["specific_diesel_consumption"] = df_enhanced_literature["specific_diesel_consumption"] * 1000
    df_enhanced_literature = df_enhanced_literature.sort_values(by="study")

#%% CONVENTIONAL model calculations

# Only this threshold is needed for conventional and climate change category
threshold_cge = [0.1]

options_ch4 = [False, True]

for option_ch4 in options_ch4:

    # Initialize class
    cge_model_s = {}
    for t in threshold_cge:
        cge_model_s[t] = ConventionalSimplifiedModel(
            setup_geothermal_gsa=setup_geothermal_gsa,
            path=path_scores_conv,
            threshold=t,
            ch4=option_ch4
        )

    # Compute
    cge_s = {}
    for t in threshold_cge:
        temp_ = {}
        for _, rows in df_conventional_literature.iterrows():
            # Values are multplied by 1000 to get gCO2 eq
            temp_[rows["study"]] = (
                cge_model_s[t].run(rows, lcia_methods=method)[method[0][-2]] * 1000
            )
        cge_s[t] = temp_

    # Re-arrange
    cge_s_df = pd.DataFrame.from_dict(cge_s)
    cge_s_df.columns = ["{:.0%}".format(t) for t in cge_s_df.columns]
    cge_s_df = cge_s_df.reset_index().rename(columns={"index": "study"})

    # Save
    filename_cge_s = "{}.{}.cc_test_cases.ch4_{}.json".format("conventional", "simplified", str(option_ch4))
    filepath_cge_s = write_dir_validation / filename_cge_s
    print("Saving {}".format(filepath_cge_s))
    cge_s_df.to_json(filepath_cge_s, double_precision=15)

#%% ENHANCED model calculations    

threshold_ege = [0.1, 0.05]

ege_model_s = {}
for t in threshold_ege:

    # Initialize class
    ege_model_s[t] = EnhancedSimplifiedModel(
        setup_geothermal_gsa=setup_geothermal_gsa,
        path=path_scores_enh,
        threshold=t,
    )

# Compute
ege_s = {}
for t in threshold_ege:
    temp_ = {}
    for _, rows in df_enhanced_literature.iterrows():
        # Values are multplied by 1000 to get gCO2 eq
        temp_[rows["study"]] = (
            ege_model_s[t].run(rows, lcia_methods=method)[method[0][-2]] * 1000
        )
    ege_s[t] = temp_

# Re-arrange
ege_s_df = pd.DataFrame.from_dict(ege_s)
ege_s_df.columns = ["{:.0%}".format(t) for t in ege_s_df.columns]
ege_s_df = ege_s_df.reset_index().rename(columns={"index": "study"})

# Save
filename_ege_s = "enhanced.simplified.cc_test_cases.json"
filepath_ege_s = write_dir_validation / filename_ege_s
print("Saving {}".format(filepath_ege_s))
ege_s_df.to_json(filepath_ege_s, double_precision=15)


