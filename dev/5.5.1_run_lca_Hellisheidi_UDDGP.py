# %% Set up
import bw2data as bd
import bw2calc as bc
import pandas as pd
from pathlib import Path

# Local files
from gsa_geothermal.utils import lookup_geothermal, create_presamples, get_EF_methods
from gsa_geothermal.general_models import GeothermalConventionalModel, GeothermalEnhancedModel
from gsa_geothermal.parameters import get_parameters

if __name__ == '__main__':
    # Set project
    bd.projects.set_current("Geothermal")

    # Method
    methods = get_EF_methods()

    # Find demand
    _, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_prod_conv, electricity_prod_enh = lookup_geothermal()

    # Save data
    write_dir_validation = Path("write_files") / "validation"
    
    # %% Set-up LCA
    # Static LCA with presamples
    options = ["hellisheidi", "uddgp"]

    for option in options:
        filename = "{}_impacts.xlsx".format(option)
        filepath = write_dir_validation / filename
        if filepath.exists():
            print("{} already exists".format(filename))
        else:
            if option == "hellisheidi":
                exploration = True
                electricity_prod = electricity_prod_conv
                ModelClass = GeothermalConventionalModel
            elif option == "uddgp":
                exploration = False
                electricity_prod = electricity_prod_enh
                ModelClass = GeothermalEnhancedModel
            success_rate = True
    
            parameters = get_parameters(option)
            model = ModelClass(parameters, exploration=exploration, success_rate=success_rate)
            parameters_sta = model.run_with_presamples(parameters)
            static_filepath = create_presamples(parameters_sta)
    
            #Do LCA
            lca = bc.LCA({electricity_prod: 1}, presamples=[static_filepath])
            lca.lci()
            sta_results = {}
            for method in methods:
                lca.switch_method(method)
                lca.lcia()
                sta_results[method] = [lca.score]
    
            sta_result_df = pd.DataFrame(sta_results).melt(
                var_name=["method_1", "method_2", "method_3"],
                value_name="impact",
            )
    
            #Write excel
            print("Saving {}".format(filepath))
            sta_result_df.to_excel(filepath)
