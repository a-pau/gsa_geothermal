#%% Set-up
import brightway2 as bw
import pandas as pd
import os
import warnings

# Import local
from utils.lookup_func import lookup_geothermal
from setup_files_gsa import setup_gt_project, get_ILCD_methods, run_mc
from cge_model import GeothermalConventionalModel
from ege_model import GeothermalEnhancedModel
from simplified_gt_models import ConventionalSimplifiedModel as cge_model_s_
from simplified_gt_models import EnhancedSimplifiedModel as ege_model_s_

from cge_klausen_test_cases import parameters_BandB_BG3, parameters_BandB_PC3, parameters_BandB_PC4, \
                            parameters_BandB_PC5, parameters_Ma, parameters_Su, parameters_Pa_SF, \
                            parameters_Pa_DF
from ege_klausen_test_cases import parameters_Fr_A1,parameters_Fr_B1, parameters_Fr_C1,\
                                   parameters_Fr_D1, parameters_LandB_base, parameters_LandB_C8,\
                                   parameters_LandB_C2, parameters_Pr, parameters_Pa_base,\
                                   parameters_Pa_2 
                            
ege_parameters = [parameters_Fr_A1,parameters_Fr_B1, parameters_Fr_C1, parameters_Fr_D1,\
                  parameters_LandB_base, parameters_LandB_C8, parameters_LandB_C2,\
                  parameters_Pr, parameters_Pa_base, parameters_Pa_2]                             
cge_parameters = [parameters_BandB_BG3, parameters_BandB_PC3, parameters_BandB_PC4, \
                 parameters_BandB_PC5, parameters_Ma, parameters_Su, parameters_Pa_SF, \
                 parameters_Pa_DF]  

# Set working directory
path = "."
os.chdir(path)

# To ignore warnings from MC (Sparse Efficiency Warning)
warnings.filterwarnings("ignore")

# Set project
bw.projects.set_current("Geothermal")

# Retrieve methods 
ILCD_CC = get_ILCD_methods(CC_only=True)

# Find demand
_, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_conv_prod, electricity_enh_prod = lookup_geothermal()

# Number of iterations
n_iter=10

# Seed for stochastic parameters
seed = 13413203

# Folder and file name for saving
ecoinvent_version = "ecoinvent_3.6"
absolute_path = os.path.abspath(path)
folder_OUT = os.path.join(absolute_path,"generated_files", ecoinvent_version, "validation")
file_name = "ReferenceVsSimplified_test_cases_CC_N" + str(n_iter)

# Load literature carbon footprints
cge_cfs=pd.read_excel(os.path.join(absolute_path, "data_and_models/Carbon footprints from literature.xlsx"), sheet_name="Conventional", index_col=None, skiprows=1)
cge_cfs=cge_cfs.dropna(subset=["Operational CO2 emissions (g/kWh)"])
cge_study_list = cge_cfs.Study.tolist()

ege_cfs=pd.read_excel(os.path.join(absolute_path, "data_and_models/Carbon footprints from literature.xlsx"), sheet_name="Enhanced", index_col=None, skiprows=1, nrows=10)
ege_study_list = ege_cfs.Study.tolist()

#%% Conventional - reference

cge_ref={}
# Reference and simplified model. Values are multplied by 1000 to get gCO2 eq.
for i, par in enumerate(cge_parameters): 
    par.stochastic(iterations=n_iter, seed=seed)     
    cge_model = GeothermalConventionalModel(par)
    cge_parameters_sto=cge_model.run_ps(par)
    temp_ = run_mc(cge_parameters_sto, {electricity_conv_prod:1}, ILCD_CC, n_iter)
    cge_ref[cge_study_list[i]] = [_*1000 for _ in temp_[ILCD_CC[0][-1]]]   

# Save    
cge_ref_df = pd.DataFrame.from_dict(cge_ref, orient="columns")
file_name_cge_ref = file_name + "_Conventional" + "_Reference" 
print("Saving ", file_name_cge_ref, " to ", folder_OUT)
cge_ref_df.to_json(os.path.join(absolute_path, folder_OUT, file_name_cge_ref))


#%% Enhanced - Reference

ege_ref={}
# Reference and simplified model. Values are multplied by 1000 to get gCO2 eq.
for i, par in enumerate(ege_parameters): 
    par.stochastic(iterations=n_iter, seed=seed)     
    ege_model = GeothermalEnhancedModel(par)
    ege_parameters_sto=ege_model.run_ps(par)
    temp_ = run_mc(ege_parameters_sto, {electricity_enh_prod:1}, ILCD_CC, n_iter)
    ege_ref[ege_study_list[i]] = [_*1000 for _ in temp_[ILCD_CC[0][-1]]]   

# Save    
ege_ref_df = pd.DataFrame.from_dict(ege_ref, orient="columns")
file_name_ege_ref = file_name + "_Enhanced" + "_Reference" 
print("Saving ", file_name_ege_ref, " to ", folder_OUT)
ege_ref_df.to_json(os.path.join(absolute_path, folder_OUT, file_name_ege_ref))

#%% Conventional - Simplified

threshold = [0.2, 0.15, 0.1, 0.05]

# Initialize classes
cge_model_s = {}
for t in threshold:
    cge_model_s[t] = cge_model_s_(t)

# Compute
cge_s = {}
for i, par in enumerate(cge_parameters):
    for t in threshold:
        par.stochastic(iterations=n_iter, seed=seed)
        temp_ = cge_model_s[t].run(par, lcia_methods=ILCD_CC)
        cge_s[cge_study_list[i]]= [_*1000 for _ in temp_[ILCD_CC[0][-1]]]

# Save
cge_s_df = pd.DataFrame.from_dict(cge_s, orient="columns")
file_name_cge_s = file_name + "_Conventional" + "_Simplified" + "_t" + str(t)
print("Saving ", file_name_cge_s, " to ", folder_OUT)
cge_s_df.to_json(os.path.join(folder_OUT, file_name_cge_s), double_precision=15)


#%% Enhanced 

# NEED TO SAVE ALL THRESHOLDS!!!
threshold = [0.2, 0.15, 0.1, 0.05]

# Initialize classes
ege_model_s = {}
for t in threshold:
    ege_model_s[t] = ege_model_s_(t)

# Compute
ege_s = {}
for i, par in enumerate(ege_parameters):
    for t in threshold:
        par.stochastic(iterations=n_iter, seed=seed)
        temp_ = ege_model_s[t].run(par, lcia_methods=ILCD_CC)
        ege_s[ege_study_list[i]]= [_*1000 for _ in temp_[ILCD_CC[0][-1]]]

# Save
ege_s_df = pd.DataFrame.from_dict(ege_s, orient="columns")
file_name_ege_s = file_name + "_Enhanced" + "_Simplified" + "_t" + str(t)
print("Saving ", file_name_ege_s, " to ", folder_OUT)
ege_s_df.to_json(os.path.join(folder_OUT, file_name_ege_s), double_precision=15)

        
