import pandas as pd
import json

cge_path = 'generated_files//gsa_results//cge_N500/sobol_indices.json'

with open(cge_path) as f:
    sa_dict = json.load(f)

parameters = sa_dict['parameters']
n_parameters = len(parameters)

# Extract total index into a dictionary and dataframe
total_dict, first_dict = {}, {}
total_dict['parameters'] = parameters
first_dict['parameters'] = parameters

for k in sa_dict.keys():
    if k != 'parameters':
        total_dict[k] = sa_dict[k]['ST']
        first_dict[k] = sa_dict[k]['S1']#[abs(a) for a in all_vals_first[n_all-n_parameters:]]

cge_total_df = pd.DataFrame(total_dict)
cge_first_df = pd.DataFrame(first_dict)


ege_path = 'generated_files//gsa_results//ege_N500/sobol_indices.json'

with open(ege_path) as f:
    sa_dict = json.load(f)

parameters = sa_dict['parameters']
n_parameters = len(parameters)

# Extract total index into a dictionary and dataframe
total_dict, first_dict = {}, {}
total_dict['parameters'] = parameters
first_dict['parameters'] = parameters

for k in sa_dict.keys():
    if k != 'parameters':
        total_dict[k] = sa_dict[k]['ST']
        first_dict[k] = sa_dict[k]['S1']#[abs(a) for a in all_vals_first[n_all-n_parameters:]]
        
ege_total_df = pd.DataFrame(total_dict)
ege_first_df = pd.DataFrame(first_dict)

with pd.ExcelWriter('generated_files//gsa_results//Sobol_indices.xlsx') as writer:  
    cge_first_df.to_excel(writer, sheet_name='CGE FIRST')
    cge_total_df.to_excel(writer, sheet_name='CGE TOTAL')
    ege_first_df.to_excel(writer, sheet_name='EGE FIRST')
    ege_total_df.to_excel(writer, sheet_name='EGE TOTAL')