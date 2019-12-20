#%% Set up
import brightway2 as bw
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
from utils.FileNameFromOptions import get_file_name
from cge_model import GeothermalConventionalModel
from cge_klausen import parameters as cge_parameters
from ege_model import GeothermalEnhancedModel
from ege_klausen import parameters as ege_parameters
from utils.Stoc_MultiMethod_LCA_pygsa import run_mc

# Method 
ILCD_CC = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)]

# Find demand
_, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_conv_prod, electricity_enh_prod = lookup_geothermal()

# Number of iterations
n_iter=100

#%% Options
exploration= True
success_rate = True

#%% Reference model

# Run model with presamples
cge_parameters.stochastic(iterations=n_iter)
cge_model = GeothermalConventionalModel(cge_parameters, exploration = exploration, success_rate = success_rate)
cge_parameters_sto=cge_model.run_ps(cge_parameters)
cge_ref = run_mc(cge_parameters_sto, electricity_conv_prod, ILCD_CC, n_iter)

cge_ref_df=pd.DataFrame.from_dict(cge_ref, orient="columns")
cge_ref_df.columns = ["carbon footprint"]
# Multiply by 1000 to get gCO2 eq.
cge_ref_df["carbon footprint"] = cge_ref_df["carbon footprint"] *1000

#%% Enhanced model

# Run model with presamples
ege_parameters.stochastic(iterations=n_iter)
ege_model = GeothermalEnhancedModel(ege_parameters, exploration = exploration, success_rate = success_rate)
ege_parameters_sto=ege_model.run_ps(ege_parameters)
ege_ref = run_mc(ege_parameters_sto, electricity_enh_prod, ILCD_CC, n_iter)

ege_ref_df=pd.DataFrame.from_dict(ege_ref, orient="columns")
ege_ref_df.columns = ["carbon footprint"]
# Multiply by 1000 to get gCO2 eq.
ege_ref_df["carbon footprint"] = ege_ref_df["carbon footprint"] *1000

#%% Save data 
file_name = "ReferenceVsLiterature CC N" + str(n_iter)
folder = "generated_files/validation_ecoinvent3.6"

print("Saving ", file_name, "in", folder)

cge_ref_df.to_json(os.path.join(absolute_path, folder, cge_file_name + " - Conventional"))
ege_ref_df.to_json(os.path.join(absolute_path, folder, ege_file_name + " - Enhanced"))
