#%% Set-up
import brightway2 as bw
import pandas as pd
import os
import warnings

# Set working directory
path = "."
os.chdir(path)
absolute_path = os.path.abspath(path)

# To ignore warnings from MC (Sparse Efficiency Warning)
warnings.filterwarnings("ignore")

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
ILCD_CC = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)][0]

# Find demand
_, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_conv_prod, electricity_enh_prod = lookup_geothermal()

# Number of iterations
n_iter=10000

# ecoinvent version
ecoinvent_version = "ecoinvent_3.6"

#%% CHOOSE OPTION

exploration = True
success_rate = True

#%% Load simplified models coefficients data
file_name = get_file_name("Simplified models coefficients - analytical.xlsx", exploration=exploration, success_rate=success_rate) 
folder_IN = os.path.join("generated_files", ecoinvent_version)

coeffs_=pd.read_excel(os.path.join(folder_IN, file_name), sheet_name=["alpha", "beta", "chi", "delta"], index_col=0, dtype=object)
alpha = coeffs_["alpha"].to_dict()
beta = coeffs_["beta"].to_dict()
chi = coeffs_["chi"].to_dict()
delta = coeffs_["delta"].to_dict()

#%% Conventional

from cge_klausen_test_cases import parameters_BandB_BG3, parameters_BandB_PC3, parameters_BandB_PC4, \
                            parameters_BandB_PC5, parameters_Ma, parameters_Su, parameters_Pa_SF, \
                            parameters_Pa_DF
                            
cge_parameters = [parameters_BandB_BG3, parameters_BandB_PC3, parameters_BandB_PC4, \
                 parameters_BandB_PC5, parameters_Ma, parameters_Su, parameters_Pa_SF, \
                 parameters_Pa_DF]  

# Load literature carbon footprints and parameters
cge_cfs=pd.read_excel(os.path.join(absolute_path, "data_and_models/Carbon footprints from literature.xlsx"), sheet_name="Conventional", index_col=None, skiprows=1)
cge_cfs=cge_cfs.dropna(subset=["Operational CO2 emissions (g/kWh)"])

cge_study_list = cge_cfs.Study.tolist()

cge_ref={}
cge_s = {}

# Reference and simplified model. Values are multplied by 1000 to get gCO2 eq.
for i, par in enumerate(cge_parameters): 
    par.stochastic(iterations=n_iter)     
    cge_model = GeothermalConventionalModel(par, exploration = exploration, success_rate = success_rate)
    cge_parameters_sto=cge_model.run_ps(par)
    temp_ = run_mc(cge_parameters_sto, electricity_conv_prod, ILCD_CC, n_iter)
    cge_ref[cge_study_list[i]] = [_*1000 for _ in temp_[ILCD_CC]]
    temp_ = simplified_cge_model(par, ILCD_CC, alpha=alpha, static=True)
    cge_s[cge_study_list[i]]= [_*1000 for _ in temp_[ILCD_CC]]
    
cge_ref_df = pd.DataFrame.from_dict(cge_ref, orient="columns")
cge_s_df = pd.DataFrame.from_dict(cge_s, orient="columns")

#%% Enhanced 

from ege_klausen_test_cases import parameters_Fr_A1,parameters_Fr_B1, parameters_Fr_C1,\
                                   parameters_Fr_D1, parameters_LandB_base, parameters_LandB_C8,\
                                   parameters_LandB_C2, parameters_Pr, parameters_Pa_base,\
                                   parameters_Pa_2 
                            
ege_parameters = [parameters_Fr_A1,parameters_Fr_B1, parameters_Fr_C1, parameters_Fr_D1,\
                  parameters_LandB_base, parameters_LandB_C8, parameters_LandB_C2,\
                  parameters_Pr, parameters_Pa_base, parameters_Pa_2]  

# Load literature carbon footprints and parameters
ege_cfs=pd.read_excel(os.path.join(absolute_path, "data_and_models/Carbon footprints from literature.xlsx"), sheet_name="Enhanced", index_col=None, skiprows=1, nrows=10)

ege_study_list = ege_cfs.Study.tolist()

ege_ref={}
ege_s = {}

# Reference and simplified model. Values are multplied by 1000 to get gCO2 eq.
for i, par in enumerate(ege_parameters): 
    par.stochastic(iterations=n_iter)     
    ege_model = GeothermalEnhancedModel(par, exploration = exploration, success_rate = success_rate)
    ege_parameters_sto=ege_model.run_ps(par)
    temp_ = run_mc(ege_parameters_sto, electricity_enh_prod, ILCD_CC, n_iter)
    ege_ref[ege_study_list[i]] = [_*1000 for _ in temp_[ILCD_CC]]
    temp_ = simplified_ege_model(par, ILCD_CC, delta=delta, static=True)
    ege_s[ege_study_list[i]]= [_*1000 for _ in temp_[ILCD_CC]]
    
ege_ref_df = pd.DataFrame.from_dict(ege_ref, orient="columns")
ege_s_df = pd.DataFrame.from_dict(ege_s, orient="columns")

#%% Write to rxcel
file_name_2 = get_file_name("ReferenceVsSimplified_test_cases CC", exploration=exploration, success_rate=success_rate) 
file_name_2 = file_name_2 + " N" + str(n_iter)
folder_OUT = os.path.join("generated_files", ecoinvent_version, "validation")

print("Saving ", file_name_2, "in", folder_OUT)

cge_ref_df.to_json(os.path.join(absolute_path, folder_OUT, file_name_2 + " - Conventional Ref"))
cge_s_df.to_json(os.path.join(absolute_path, folder_OUT, file_name_2 +  " - Conventional Sim"))
ege_ref_df.to_json(os.path.join(absolute_path, folder_OUT, file_name_2 + " - Enhanced Ref"))
ege_s_df.to_json(os.path.join(absolute_path, folder_OUT, file_name_2 + " - Enhanced Sim"))

        
        
