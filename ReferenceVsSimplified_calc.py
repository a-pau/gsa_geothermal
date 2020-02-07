#%% Set-up

import brightway2 as bw
import pandas as pd
import os
import warnings

# Set working directry
path = "."
os.chdir(path)

# Import local
from cge_klausen import parameters as cge_parameters
from ege_klausen import parameters as ege_parameters
from cge_model import GeothermalConventionalModel
from ege_model import GeothermalEnhancedModel
from s_models import simplified_cge_model, simplified_ege_model
from utils.lookup_func import lookup_geothermal
from utils.Stoc_MultiMethod_LCA_pygsa import run_mc

# Set project
bw.projects.set_current("Geothermal")

# Retrieve methods 
ILCD_CC = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)]
ILCD_HH = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "human health" in str(method)]
ILCD_EQ = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "ecosystem quality" in str(method)]
ILCD_RE = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "resources" in str(method)]
ILCD = ILCD_CC + ILCD_HH + ILCD_EQ + ILCD_RE

# Find demand
_, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_conv_prod, electricity_enh_prod = lookup_geothermal()

# Number of iterations
n_iter=10000

# ecoinvent version
ecoinvent_version = "ecoinvent_3.6"

# Load simplified models coefficients
absolute_path = os.path.abspath(path)
folder_IN = os.path.join("generated_files", ecoinvent_version)

coeffs_=pd.read_excel(os.path.join(absolute_path, folder_IN, "Simplified models coefficients - analytical.xlsx"), sheet_name=["alpha", "beta", "chi", "delta"], index_col=0, dtype=object)
alpha = coeffs_["alpha"].to_dict()
beta = coeffs_["beta"].to_dict()
chi = coeffs_["chi"].to_dict()
delta = coeffs_["delta"].to_dict()

# To ignore warnings from MC (Sparse Efficiency Warning)
warnings.filterwarnings("ignore")

#%% Conventional model calculations

# Generate stochastic values
cge_parameters.stochastic(iterations=n_iter)

# Reference model
cge_model = GeothermalConventionalModel(cge_parameters)
cge_parameters_sto = cge_model.run_ps(cge_parameters)
ref_cge = run_mc(cge_parameters_sto, electricity_conv_prod, ILCD, n_iter)

# Simplified model
s_cge = simplified_cge_model(cge_parameters, ILCD, alpha, beta)

ref_cge_df=pd.DataFrame.from_dict(ref_cge, orient="columns").melt(var_name=["method_1", "method_2", "method_3"],value_name="Reference")
s_cge_df=pd.DataFrame.from_dict(s_cge, orient="columns").melt(var_name=["method_1", "method_2", "method_3"], value_name="Simplified")
cge_df = pd.merge(ref_cge_df, s_cge_df["Simplified"], how="left", left_index=True, right_index=True)

#%% Enhanced model calculations

# Generate stochastic values
ege_parameters.stochastic(iterations=n_iter)

# Reference model
ege_model = GeothermalEnhancedModel(ege_parameters)
ege_parameters_sto=ege_model.run_ps(ege_parameters)
ref_ege = run_mc(ege_parameters_sto, electricity_enh_prod, ILCD, n_iter)

# Simplified model
s_ege=simplified_ege_model(ege_parameters, ILCD, chi, delta)

ref_ege_df=pd.DataFrame.from_dict(ref_ege, orient="columns").melt(var_name=["method_1", "method_2", "method_3"],value_name="Reference")
s_ege_df=pd.DataFrame.from_dict(s_ege, orient="columns").melt(var_name=["method_1", "method_2", "method_3"], value_name="Simplified")
ege_df = pd.merge(ref_ege_df, s_ege_df["Simplified"], how="left", left_index=True, right_index=True)

    
#%% Save data
file_name = "ReferenceVsSimplified N" + str(n_iter)
folder_OUT = os.path.join("generated_files", ecoinvent_version, "validation")

print("Saving ", file_name, "in", folder_OUT)

cge_df.to_json(os.path.join(absolute_path, folder_OUT, file_name + " - Conventional"), double_precision=15)
ege_df.to_json(os.path.join(absolute_path, folder_OUT, file_name + " - Enhanced"), double_precision=15)
       