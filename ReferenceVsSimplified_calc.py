#%% SETUP

import brightway2 as bw
import pandas as pd
import os
import warnings

from utils.lookup_func import lookup_geothermal
from setup_files_gsa import setup_gt_project, get_ILCD_methods, run_mc
from cge_klausen import get_parameters as get_cge_parameters
from ege_klausen import get_parameters as get_ege_parameters
from cge_model import GeothermalConventionalModel
from ege_model import GeothermalEnhancedModel
from simplified_gt_models import ConventionalSimplifiedModel as cge_model_s_
from simplified_gt_models import EnhancedSimplifiedModel as ege_model_s_

# Set working directry
path = "."
os.chdir(path)

# Set project
bw.projects.set_current("Geothermal")

# Find demand
_, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_conv_prod, electricity_enh_prod = lookup_geothermal()

# Get methods
ILCD = get_ILCD_methods()

# Number of iterations
n_iter = 10000

# Seed for stochastic parameters
seed = 13413203

# Folder and file name for saving
ecoinvent_version = "ecoinvent_3.6"
absolute_path = os.path.abspath(path)
folder_OUT = os.path.join(absolute_path,"generated_files", ecoinvent_version, "validation")
file_name = "ReferenceVsSimplified_N" + str(n_iter)

# To ignore warnings from MC (Sparse Efficiency Warning)
warnings.filterwarnings("ignore")

# Get parameters
cge_parameters = get_cge_parameters()
ege_parameters = get_ege_parameters()

#%% CONVENTIONAL model calculations - REFERENCE

# Generate stochastic values
cge_parameters.stochastic(iterations=n_iter, seed=seed)

# Compute
cge_model = GeothermalConventionalModel(cge_parameters)
cge_parameters_sto = cge_model.run_ps(cge_parameters)
cge_ref = run_mc(cge_parameters_sto, {electricity_conv_prod:1}, ILCD, n_iter)

# Save
cge_ref_df = pd.DataFrame.from_dict(cge_ref)

file_name_cge_ref = file_name + "_Conventional" + "_Reference"
print("Saving ", file_name_cge_ref, "\nto\n", folder_OUT)
cge_ref_df.to_json(os.path.join(folder_OUT, file_name_cge_ref), double_precision=15)

#%% ENHANCED model calculations - REFERENCE
# Generate stochastic values
ege_parameters.stochastic(iterations=n_iter, seed=seed)

# Compute
ege_model = GeothermalEnhancedModel(ege_parameters)
ege_parameters_sto = ege_model.run_ps(ege_parameters)
ege_ref = run_mc(ege_parameters_sto, {electricity_enh_prod:1}, ILCD, n_iter)

# Save
ege_ref_df = pd.DataFrame.from_dict(ege_ref)

file_name_ege_ref = file_name + "_Enhanced" + "_Reference"
print("Saving ", file_name_ege_ref, "\nto\n", folder_OUT)
ege_ref_df.to_json(os.path.join(folder_OUT, file_name_ege_ref), double_precision=15)

#%%CONVENTIONAL model calculations - SIMPLIFIED

threshold = [0.2, 0.15, 0.1, 0.05]

cge_parameters.stochastic(iterations=n_iter, seed=seed)

for t in threshold:
    
    # Initialize class
    cge_model_s = cge_model_s_(t)

    # Compute 
    cge_s = cge_model_s.run(cge_parameters)
    
    # Save
    cge_s_df = pd.DataFrame.from_dict(cge_s)
    file_name_cge_s = file_name + "_Conventional" + "_Simplified" + "_t" + str(t)
    print("Saving ", file_name_cge_s, "\nto\n", folder_OUT)
    cge_s_df.to_json(os.path.join(folder_OUT, file_name_cge_s), double_precision=15)
    
#%%ENHANCED model calculations - SIMPLIFIED

threshold = [0.2,0.15, 0.1, 0.05]

ege_parameters.stochastic(iterations=n_iter, seed=seed)

for t in threshold:
    
    # Initialize class
    ege_model_s = ege_model_s_(t)
    
    # Compute 
    ege_s = ege_model_s.run(ege_parameters)
    
    # Save
    ege_s_df = pd.DataFrame.from_dict(ege_s)
    file_name_ege_s = file_name + "_Enhanced" + "_Simplified" + "_t" + str(t)
    print("Saving ", file_name_ege_s, "\nto\n", folder_OUT)
    ege_s_df.to_json(os.path.join(folder_OUT, file_name_ege_s), double_precision=15)
