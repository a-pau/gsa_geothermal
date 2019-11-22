#%% Set-up

import brightway2 as bw
import seaborn as sb
import matplotlib.pyplot as plt
import numpy as np
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

# Set project
bw.projects.set_current("Geothermal")

# Retrieve methods 
ILCD_CC = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)][0]

# Find demand
_, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_conv_prod, electricity_enh_prod = lookup_geothermal()

# Number of iterations
n_iter=100

# Load simplified models coefficients
coeffs_=pd.read_excel(os.path.join(absolute_path, "generated_files/Simplified models coefficients - analytical.xlsx"), sheet_name=["alpha", "beta", "chi", "delta"], index_col=0, dtype=object)
alpha = coeffs_["alpha"].to_dict()
beta = coeffs_["beta"].to_dict()
chi = coeffs_["chi"].to_dict()
delta = coeffs_["delta"].to_dict()

# To ignore warnings from MC (Sparse Efficiency Warning)
warnings.filterwarnings("ignore")

#%% Conventional

from cge_klausen_test_cases import parameters_BandB_BG3, parameters_BandB_PC3, parameters_BandB_PC4, \
                            parameters_BandB_PC5, parameters_Ma, parameters_Su, parameters_Pa_SF, \
                            parameters_Pa_DF
                            
cge_parameters = [parameters_BandB_BG3, parameters_BandB_PC3, parameters_BandB_PC4, \
                 parameters_BandB_PC5, parameters_Ma, parameters_Su, parameters_Pa_SF, \
                 parameters_Pa_DF]  

# Load literature carbon footprints and parameters
cge_cfs=pd.read_excel(os.path.join(absolute_path, "data_and_models/Carbon footprints from literature.xlsx"), sheet_name="Conventional", index_col=None, skiprows=1)
cge_cfs=cfs.dropna(subset=["Operational CO2 emissions (g/kWh)"])

cge_study_list = cfs.Study.tolist()

cge_ref={}
cge_s = {}

# Reference and simplified model. Values are multplied by 1000 to get gCO2 eq.
for i, par in enumerate(cge_parameters): 
    par.stochastic(iterations=n_iter)     
    cge_model = GeothermalConventionalModel(par)
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
    ege_model = GeothermalEnhancedModel(par)
    ege_parameters_sto=ege_model.run_ps(par)
    temp_ = run_mc(ege_parameters_sto, electricity_enh_prod, ILCD_CC, n_iter)
    ege_ref[ege_study_list[i]] = [_*1000 for _ in temp_[ILCD_CC]]
    temp_ = simplified_ege_model(par, ILCD_CC, delta=delta, static=True)
    ege_s[ege_study_list[i]]= [_*1000 for _ in temp_[ILCD_CC]]
    
ege_ref_df = pd.DataFrame.from_dict(ege_ref, orient="columns")
ege_s_df = pd.DataFrame.from_dict(ege_s, orient="columns")

#%% Write to rxcel
with pd.ExcelWriter(os.path.join(absolute_path, 'generated_files/Carbon footprint - test cases.xlsx')) as writer:
        cge_ref_df.to_excel(writer, sheet_name="conventional reference model")
        cge_s_df.to_excel(writer, sheet_name='conventional simplified model')
        ege_ref_df.to_excel(writer, sheet_name="enhanced reference model")
        ege_s_df.to_excel(writer, sheet_name='enhanced simplified model')
        
        
