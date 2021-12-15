#%% Set up
import brightway2 as bw
import pandas as pd
import os

# Set working directory
path = "../dev"
os.chdir(path)
absolute_path = os.path.abspath(path)

# Set project
bw.projects.set_current("Geothermal")

# Import local
from utils.lookup_func import lookup_geothermal
from ege_model import GeothermalEnhancedModel
from ege_klausen_UDDGP import parameters
from utils.Create_Presamples_File import create_presamples


# Method 
ILCD_CC = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)]
ILCD_HH = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "human health" in str(method)]
ILCD_EQ = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "ecosystem quality" in str(method)]
ILCD_RE = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "resources" in str(method)]
ILCD = ILCD_CC + ILCD_HH + ILCD_EQ + ILCD_RE

# Find demand
_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_prod = lookup_geothermal()

#%%Options
exploration= False
success_rate = True

#%% Set-up LCA
# Static LCA with presamples
parameters.static()
model = GeothermalEnhancedModel(parameters, exploration=exploration, success_rate=success_rate)
parameters_sta=model.run_with_presamples(parameters)
static_filepath = create_presamples(parameters_sta)

#%% Do LCA
lca = bw.LCA({electricity_prod: 1}, presamples=[static_filepath])
lca.lci()
sta_results={}
for method in ILCD:
    lca.switch_method(method)
    lca.lcia()
    sta_results[method]=[lca.score]

sta_result_df = pd.DataFrame(sta_results).melt(var_name=["method_1", "method_2", "method_3"], value_name="impact")

#%% Write excel
file_name = os.path.join(absolute_path, "generated_files", "ecoinvent_3.6", "UDDGP impacts.xlsx")
sta_result_df.to_excel(file_name)
