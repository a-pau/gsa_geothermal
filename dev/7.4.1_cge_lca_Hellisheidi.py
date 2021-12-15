#%% Set up
import brightway2 as bw
import presamples as ps
import seaborn as sb
import pandas as pd
import os

# Set working directory
path = "."
os.chdir(path)
absolute_path = os.path.abspath(path)

# Set project
bw.projects.set_current("Geothermal")

# Import local
from utils.lookup_func import lookup_geothermal
from cge_model import GeothermalConventionalModel
from cge_klausen_Hellisheidi import parameters
from utils.Create_Presamples_File import create_presamples

# Method 
ILCD_CC = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)]
ILCD_HH = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "human health" in str(method)]
ILCD_EQ = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "ecosystem quality" in str(method)]
ILCD_RE = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "resources" in str(method)]
ILCD = ILCD_CC + ILCD_HH + ILCD_EQ + ILCD_RE

# Find demand
_, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_prod, _ = lookup_geothermal()

#Options
exploration=True
success_rate = True

#%% Set-up LCA
# Static LCA with presamples
parameters.static()
model = GeothermalConventionalModel(parameters, exploration=exploration, success_rate=success_rate)
parameters_sta=model.run_with_presamples(parameters)
static_filepath = create_presamples(parameters_sta)

#%% Do LCA
lca = bw.LCA({electricity_prod: 1}, presamples=[static_filepath])  # TODO Sasha
lca.lci()
sta_results={}
for method in ILCD:
    lca.switch_method(method)
    lca.lcia()
    sta_results[method]=[lca.score]

sta_result_df = pd.DataFrame(sta_results).melt(var_name=["method_1", "method_2", "method_3"], value_name="impact")

#%% Write excel
file_name = os.path.join(absolute_path, "generated_files", "Hellisheidi impacts.xlsx")
sta_result_df.to_excel(file_name)

#%% Other ....
# Contribution analysis
electricity_prod_act = bw.Database("geothermal energy").get(electricity_prod[1])

contributions_extr = []
contributions = []
sta_results={}
for method in ILCD:
    lca.switch_method(method)
    lca.lcia()
    sta_results[method]=lca.score
    dict_1 = {k:v for k,v in recursive_calculator(lca, electricity_prod_act, 1, sta_results[method], max_depth=2).items()}
    dict_1["method"]= str(method)
    contributions.append(dict_1)
    dict_1_extr = {k:v for k,v in  extract_act(dict_1, 2, direct=True).items()}
    dict_1_extr["method"]= str(method)
    contributions_extr.append(dict_1_extr)

data_frame = json_normalize(data=contributions_extr, record_path="chain", meta=["method", "activity", "score", "depth"], record_prefix="chain.")

#Normalisation
sta_results_norm = {}
for method in sta_results:
    print(method[2], sta_results[method], "/", NormalisationFactors_dict[method]["per Person"], "=", sta_results[method]/NormalisationFactors_dict[method]["per Person"])
    sta_results_norm[method[2]] = sta_results[method]/NormalisationFactors_dict[method]["per Person"]
#plot
sb.barplot(y = list(sta_results_norm.keys()), x = list(sta_results_norm.values()))
