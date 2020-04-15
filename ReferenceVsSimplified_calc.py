#%% SETUP

import brightway2 as bw
import pandas as pd
import os
import warnings
from setup_files_gsa import setup_gt_project, get_ILCD_methods, run_mc
from simplified_gt_models import ConventionalSimplifiedModel as cge_model_s_

# Set working directry
path = "."
os.chdir(path)

# Get models and parameters
project = 'Geothermal'
option = 'cge'
electricity_conv_prod, cge_model, cge_parameters = setup_gt_project(project, option)

# Get methods
ILCD = get_ILCD_methods()

# Number of iterations
n_iter = 500

# Seed for stochastic parameters
seed = 13413203

# Folder and file name for saving
ecoinvent_version = "ecoinvent_3.6"
absolute_path = os.path.abspath(path)
folder_OUT = os.path.join(absolute_path,"generated_files", ecoinvent_version, "validation")
file_name = "ReferenceVsSimplified_N" + str(n_iter)

# To ignore warnings from MC (Sparse Efficiency Warning)
#warnings.filterwarnings("ignore")

#%% Conventional model calculations - reference

# Generate stochastic values
cge_parameters.stochastic(iterations=n_iter, seed=seed)

# Compute
cge_parameters_sto = cge_model.run_ps(cge_parameters)
ref_cge = run_mc(cge_parameters_sto, electricity_conv_prod, ILCD, n_iter)

# Save
ref_cge_df = pd.DataFrame.from_dict(ref_cge)

file_name_cge_ref = file_name + "_Conventional" + "_Reference"
print("Saving ", file_name_cge_ref, " to ", folder_OUT)
ref_cge_df.to_json(os.path.join(folder_OUT, file_name_cge_ref), double_precision=15)

#%%Conventional model calculations - simplified
threshold = 0.2     # 20%

# Initialize class
cge_model_s = cge_model_s_(threshold)

# TODO once "static" is fixed in simplified_models, this can be removed.
cge_parameters.stochastic(iterations=n_iter, seed=seed)

# Compute 
s_cge = cge_model_s.run(cge_parameters)

# Save
s_cge_df = pd.DataFrame.from_dict(s_cge)
file_name_cge_s = file_name + "_Conventional" + "_Simplified"
print("Saving ", file_name_cge_s, " to ", folder_OUT)
s_cge_df.to_json(os.path.join(folder_OUT, file_name_cge_s), double_precision=15)




####### TO BE COMPLETED #######
