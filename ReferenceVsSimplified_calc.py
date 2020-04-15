#%% SETUP

import brightway2 as bw
import pandas as pd
import os
import warnings
from setup_files_gsa import setup_gt_project, run_mc
from simplified_gt_models import ConventionalSimplifiedModel as cge_model_s_

# Set working directry
path = "."
os.chdir(path)

# 
project = 'Geothermal'
option = 'cge'
electricity_conv_prod, ILCD_CC , cge_model, cge_parameters = setup_gt_project(project, option, CC_only=True)

# Number of iterations
n_iter = 10

# Seed for stochastic parameters
seed = 13413203

# Folder and file name for saving
ecoinvent_version = "ecoinvent_3.6"
absolute_path = os.path.abspath(path)
folder_OUT = os.path.join(absolute_path,"generated_files", ecoinvent_version, "validation")
file_name = "ReferenceVsSimplified N" + str(n_iter)


# To ignore warnings from MC (Sparse Efficiency Warning)
warnings.filterwarnings("ignore")

#%% Conventional model calculations - reference

# Generate stochastic values
cge_parameters.stochastic(iterations=n_iter, seed=seed)

# Reference model
cge_parameters_sto = cge_model.run_ps(cge_parameters)
ref_cge = run_mc(cge_parameters_sto, electricity_conv_prod, ILCD_CC, n_iter)

# Save
ref_cge_df = pd.DataFrame.from_dict(ref_cge)
path_and_full_name = os.path.join(folder_OUT, file_name + "-Reference" + "-Conventional.txt")
ref_cge_df.to_json(path_and_full_name, double_precision=15)

#%%Conventional model calculations - simplified
threshold = 0.2     # 20%
cge_model_s = cge_model_s_(threshold)

cge_parameters.stochastic(iterations=n_iter, seed=seed)
s_cge = cge_model_s.run(cge_parameters, lcia_methods=ILCD_CC)

# Save
s_cge_df = pd.DataFrame.from_dict(s_cge)
path_and_full_name = os.path.join(folder_OUT, file_name + "-Simplified" + "-Conventional.txt")
s_cge_df.to_json(path_and_full_name, double_precision=15)





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
       