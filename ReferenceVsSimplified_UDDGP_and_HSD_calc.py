#%% Set-up

import brightway2 as bw
import pandas as pd
import os
import warnings

# Set working directory
path = "."
os.chdir(path)
absolute_path = os.path.abspath(path)

# Import local
from cge_model import GeothermalConventionalModel
from ege_model import GeothermalEnhancedModel
from s_models import simplified_cge_model, simplified_ege_model
from utils.lookup_func import lookup_geothermal
from utils.Stoc_MultiMethod_LCA_pygsa import run_mc
from utils.FileNameFromOptions import get_file_name

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
n_iter=1000

# To ignore warnings from MC (Sparse Efficiency Warning)
warnings.filterwarnings("ignore")

#%% CHOOSE OPTION

exploration = True
success_rate = True

file_name = get_file_name("Simplified models coefficients - analytical.xlsx", exploration=exploration, success_rate=success_rate) 

# Load simplified models coefficients. Choose file name!
coeffs_=pd.read_excel(os.path.join(absolute_path, "generated_files", file_name), sheet_name=["alpha", "beta", "chi", "delta"], index_col=0, dtype=object)
alpha = coeffs_["alpha"].to_dict()
beta = coeffs_["beta"].to_dict()
chi = coeffs_["chi"].to_dict()
delta = coeffs_["delta"].to_dict()

#%% Conventional model computations

from cge_klausen_test_cases import parameters_Pa_DF_all

# Reference and simplified model. Values are multplied by 1000 to get gCO2 eq.
parameters_Pa_DF_all.stochastic(iterations=n_iter)     
cge_model = GeothermalConventionalModel(parameters_Pa_DF_all, exploration = exploration, success_rate = success_rate)
cge_parameters_sto=cge_model.run_ps(parameters_Pa_DF_all)

# Time for one iteration of run_mc is ~ 43 sec 
cge_ref = run_mc(cge_parameters_sto, electricity_conv_prod, ILCD, n_iter)   
cge_s = simplified_cge_model(parameters_Pa_DF_all, ILCD, alpha=alpha, beta=beta, static=True)

cge_ref_df = pd.DataFrame.from_dict(cge_ref, orient="columns").melt(var_name=["method_1", "method_2", "method_3"],value_name="impact score")
cge_s_df = pd.DataFrame.from_dict(cge_s, orient="columns").melt(var_name=["method_1", "method_2", "method_3"],value_name="simplified")

#%% Enhanced model computations

from ege_klausen_test_cases import parameters_Pa_base_all

# Reference and simplified model. Values are multplied by 1000 to get gCO2 eq.
parameters_Pa_base_all.stochastic(iterations=n_iter)     
ege_model = GeothermalEnhancedModel(parameters_Pa_base_all, exploration = exploration, success_rate = success_rate)
ege_parameters_sto=ege_model.run_ps(parameters_Pa_base_all)

# Time for one iteration of run_mc is ~ 43 sec 
ege_ref = run_mc(ege_parameters_sto, electricity_enh_prod, ILCD, n_iter)   
ege_s = simplified_ege_model(parameters_Pa_base_all, ILCD, chi=chi, delta=delta, static=True)

ege_ref_df = pd.DataFrame.from_dict(ege_ref, orient="columns").melt(var_name=["method_1", "method_2", "method_3"],value_name="impact score")
ege_s_df = pd.DataFrame.from_dict(ege_s, orient="columns").melt(var_name=["method_1", "method_2", "method_3"],value_name="simplified")

#%% Save data
file_name = get_file_name("ReferenceVsSmplified_UDDGP_and_HSD", exploration=exploration, success_rate=success_rate)
file_name = file_name + " N" + str(n_iter)   
print("Saving ", file_name)

cge_ref_df.to_json(os.path.join(absolute_path, "generated_files", file_name+ " - Conventional Ref"))
cge_s_df.to_json(os.path.join(absolute_path, "generated_files", file_name +  " - Conventional Sim"))
ege_ref_df.to_json(os.path.join(absolute_path, "generated_files", file_name + " - Enhanced Ref"))
ege_s_df.to_json(os.path.join(absolute_path, "generated_files", file_name + " - Enhanced Sim"))

           
        