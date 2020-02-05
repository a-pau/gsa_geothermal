# This script calculated coefficients for simplified models based on the formulas 
# in the spreadsheet "Model, parameters and uncertainty".

import brightway2 as bw
import pandas as pd
import numpy as np
import os

# Set working directry
path = "."
os.chdir(path)
absolute_path = os.path.abspath(path)

# Local functions
from utils.lookup_func import lookup_geothermal
from utils.FileNameFromOptions import get_file_name

# Set project
bw.projects.set_current("Geothermal")

# Ecoinvent version
ecoinvent = "ecoinvent 3.6 cutoff"

# Retrieve activities
wellhead, diesel, steel, cement, water, \
drilling_mud, drill_wst, wells_closr, coll_pipe, \
plant, ORC_fluid, ORC_fluid_wst, diesel_stim, co2,_, _ = lookup_geothermal(ecoinvent = ecoinvent)
cooling_tower=bw.Database("geothermal energy").search("cooling tower")[0].key

list_act = [wellhead, diesel, steel, cement, water, 
         drilling_mud, drill_wst, wells_closr, coll_pipe,
         plant, cooling_tower, ORC_fluid, ORC_fluid_wst, diesel_stim]

# Retrieve methods 
ILCD_CC = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)]
ILCD_HH = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "human health" in str(method)]
ILCD_EQ = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "ecosystem quality" in str(method)]
ILCD_RE = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "resources" in str(method)]
ILCD = ILCD_CC + ILCD_HH + ILCD_EQ + ILCD_RE

# Calculate impact of activities
lca = bw.LCA({list_act[0]: 1}, ILCD[0])
lca.lci()
lca.lcia()
coeff = {}
for method in ILCD:
    s=[]
    lca.switch_method(method)
    for act in list_act:
        lca.redo_lcia({act: 1})
        s.append(lca.score)
    coeff[method] = s

# Retrieve CF for co2 emissions    
for method in ILCD:
    CFs = bw.Method(method).load()
    coeff[method].append(next((cf[1] for cf in CFs if cf[0]==co2),0))

#Constant
drilling_waste_per_metre = 450

# Build matrix
col_names = ["wellhead", "diesel", "steel", "cement", "water", \
         "drilling_mud", "drill_wst", "wells_closr", "coll_pipe", \
         "plant", "cooling tower", "ORC_fluid", "ORC_fluid_wst", "diesel_stim", "co2"]
coeff_matrix = pd.DataFrame.from_dict(coeff, orient="index", columns=col_names)

# Re-arrange matrix
coeff_matrix["concrete"] = coeff_matrix["cement"] + coeff_matrix["water"] * 1/0.65
coeff_matrix["ORC_fluid_tot"] = coeff_matrix["ORC_fluid"] - coeff_matrix["ORC_fluid_wst"]
coeff_matrix["electricity_stim"] = coeff_matrix["diesel_stim"] * 3.6 
coeff_matrix["drill_wst"] = coeff_matrix["drill_wst"] * -1 * drilling_waste_per_metre
coeff_matrix=coeff_matrix.drop(columns=["cement", "ORC_fluid", "ORC_fluid_wst", "diesel_stim"])

col_ord = ["wellhead", "diesel", "steel", "concrete", \
         "drilling_mud", "drill_wst", "wells_closr", "coll_pipe", \
         "plant", "cooling tower", "ORC_fluid_tot", "water", "electricity_stim", "co2"]
coeff_matrix=coeff_matrix[col_ord]

is_= ["i1", "i2.1", "i2.2", "i2.3", "i2.4", "i2.5", \
      "i2.6","i3", "i4.1", "i4.2", "i4.3", "i5.1", "i5.2", "i6"]

if len(coeff_matrix.columns) == len(is_):
    coeff_matrix.columns=is_

#%% SET OPTIONS
    
exploration = True
success_rate = True
        
#%% Conventional geothermal
# Klausen
from cge_klausen import parameters
parameters.static()    

# Rename parameters (in accordance with parametric model)
P_ne=parameters["installed_capacity"]
PW_ne=parameters["gross_power_per_well"]
PI_ratio=parameters["production_to_injection_ratio"]
D_i=parameters["initial_harmonic_decline_rate"]
LT=parameters["lifetime"]
D = parameters["specific_diesel_consumption"]
C_S = parameters["specific_steel_consumption"]
C_C = parameters["specific_cement_consumption"]
DM = parameters["specific_drilling_mud_consumption"]
W_d = parameters["average_depth_of_wells"]
CP = parameters["collection_pipelines"]
CF = parameters["capacity_factor"]
A_p = parameters["auxiliary_power"]
E_co2 = parameters["co2_emissions"]

if exploration:
    W_e_en = 3 * 0.3
else:
    W_e_en = 0
    
if success_rate:
    SR_pi=parameters["success_rate_primary_wells"]/100
    SR_m=parameters["success_rate_makeup_wells"]/100
    SR_e=parameters["success_rate_exploration_wells"]/100
else:
    SR_pi=1
    SR_m=1
    SR_e=1


# Constants
CT_el = 864
CT_n = 7/303.3

a1 = P_ne * ( (PI_ratio+1) / (PI_ratio * SR_pi) + (D_i*LT/SR_m) )
b1 = W_e_en/SR_e

c1 = (P_ne *  CF * (1-A_p) * LT * 8760000) 
d1 = (CT_el * CT_n *1000 * 30)
den1= (c1-d1)

# Calculate coefficients
alpha1, alpha2, beta1, beta2, beta3, beta4 = {},{},{},{},{},{}
for method, row in coeff_matrix.iterrows():
    if method == ILCD_CC[0]:
        alpha1[method]= row["i6"]
        num = (a1/PW_ne) * ( W_d * (D*row["i2.1"] + C_S*row["i2.2"] + C_C*row["i2.3"] + DM * row["i2.4"] + row["i2.5"] + row["i2.6"]) \
               +  row["i1"] + CP * row["i3"] ) \
               + W_d * b1 * (D*row["i2.1"] + C_S*row["i2.2"] + C_C*row["i2.3"] + DM * row["i2.4"] + row["i2.5"] + row["i2.6"]) \
               + b1 * row["i1"] + P_ne * ( row["i4.1"] + row["i4.2"] * CT_n )
        alpha2[method]= num / den1                           
    else:
        num = a1 * (D*row["i2.1"] + C_S*row["i2.2"] + C_C*row["i2.3"] + DM * row["i2.4"] + row["i2.5"] + row["i2.6"])
        beta1[method] = num/den1
        num = a1 * ( row["i1"] + CP * row["i3"] )
        beta2[method] = num/den1
        num = b1 * (D*row["i2.1"] + C_S*row["i2.2"] + C_C*row["i2.3"] + DM * row["i2.4"] + row["i2.5"] + row["i2.6"]) 
        beta3[method] = num / den1
        beta4[method] = ( b1 * row["i1"] + P_ne * ( row["i4.1"] + row["i4.2"] * CT_n ) ) / den1 + (E_co2 * row["i6"])       

#%% Enhanced geothermal
# Klausen
from ege_klausen import parameters
parameters.static()   

LT=parameters["lifetime"]
D = parameters["specific_diesel_consumption"]
C_S = parameters["specific_steel_consumption"]
C_C = parameters["specific_cement_consumption"]
DM = parameters["specific_drilling_mud_consumption"]
W_d = parameters["average_depth_of_wells"]
CP = parameters["collection_pipelines"]
CF = parameters["capacity_factor"]
A_p = parameters["auxiliary_power"]
# W_pi_n = parameters["number_of_wells"] 
# Set static value of number of wells to the actual (non-integer) average.
W_pi_n = 2.5
SW_n = 0.5 + parameters["number_of_wells_stimulated_0to1"] * W_pi_n
S_w = parameters["water_stimulation"]
S_el = (parameters["specific_electricity_stimulation"]/ 1000)

if exploration:
    W_e_en = 3 * 0.3
else:
    W_e_en = 0
    
if success_rate:
    SR_pi=parameters["success_rate_primary_wells"]/100
    SR_e=parameters["success_rate_exploration_wells"]/100
else:
    SR_pi=1
    SR_e=1

# Constants
CT_el = 864
CT_n = 7/303.3
OF = 300

a2 = (W_pi_n / SR_pi) + (W_e_en / SR_e)
c2 = (CF * (1-A_p) * LT * 8760000) 
d2 = (CT_el * CT_n *1000 * 30)
  
class1 = ["carcinogenic effects", "non-carcinogenic effects", "respiratory effects, inorganics", \
          "freshwater ecotoxicity", "freshwater eutrophication", "dissipated water", 
          "land use", "minerals and metals"]

class2 = ["climate change total", "ionising radiation", "ozone layer depletion", \
          "photochemical ozone creation", "freshwater and terrestrial acidification", \
          "marine eutrophication", "terrestrial eutrophication", "fossils"]

chi1, chi2, chi3, chi4, chi5, \
delta1, delta2, delta3, delta4, delta5 = {},{},{},{},{},{},{},{},{},{}
chi3_ws, delta3_ws = {},{}
a={}
for method, row in coeff_matrix.iterrows():
    if method[2] in class1 :
        chi1[method] = a2 * (D*row["i2.1"] + C_S*row["i2.2"] + C_C*row["i2.3"] + DM * row["i2.4"] + row["i2.5"] + row["i2.6"])
        chi2[method] = row["i4.1"] + row["i4.2"] * CT_n + row["i4.3"] * OF
        chi3[method] = ( a2 * row["i1"] ) + ((W_pi_n / SR_pi) * CP * row["i3"]) + ( SW_n * S_w * ( row["i5.1"] + S_el * row["i5.2"] ) )
        #chi3_ws[method] = ( a2 * row["i1"] ) + ((W_pi_n / SR_pi) * CP * row["i3"])
        chi4[method] = c2
        chi5[method] = d2
    elif method[2] in class2:
        delta1[method] = W_d * a2 * row["i2.1"]
        delta2[method] = row["i4.1"] + row["i4.2"] * CT_n + row["i4.3"] * OF
        delta3[method] = W_d * a2 * (C_S*row["i2.2"] + C_C*row["i2.3"] + DM * row["i2.4"] + row["i2.5"] + row["i2.6"]) \
                         + (a2 * row["i1"]) + ( (W_pi_n / SR_pi) * CP * row["i3"] ) + ( SW_n * S_w * ( row["i5.1"] + S_el * row["i5.2"] ))
        #delta3_ws[method] = W_d * a2 * (C_S*row["i2.2"] + C_C*row["i2.3"] + DM * row["i2.4"] + row["i2.5"] + row["i2.6"]) \
                        # + (a2 * row["i1"]) + ( (W_pi_n / SR_pi) * CP * row["i3"] )
        delta4[method] = c2
        delta5[method] = d2
        
#%% Write coeff DataFrames to excel

# Created DataFrame for export
alpha1_df = pd.DataFrame.from_dict(alpha1, orient="index", columns=["alpha1"])
alpha2_df = pd.DataFrame.from_dict(alpha2, orient="index", columns=["alpha2"])
alpha_df = pd.concat([alpha1_df, alpha2_df], axis=1)

beta1_df = pd.DataFrame.from_dict(beta1, orient="index", columns=["beta1"])
beta2_df = pd.DataFrame.from_dict(beta2, orient="index", columns=["beta2"])
beta3_df = pd.DataFrame.from_dict(beta3, orient="index", columns=["beta3"])
beta4_df = pd.DataFrame.from_dict(beta4, orient="index", columns=["beta4"])
beta_df = pd.concat([beta1_df, beta2_df, beta3_df, beta4_df], axis=1)
       
chi1_df = pd.DataFrame.from_dict(chi1, orient="index", columns=["chi1"])
chi2_df = pd.DataFrame.from_dict(chi2, orient="index", columns=["chi2"])
chi3_df = pd.DataFrame.from_dict(chi3, orient="index", columns=["chi3"])
chi4_df = pd.DataFrame.from_dict(chi4, orient="index", columns=["chi4"])
chi5_df = pd.DataFrame.from_dict(chi5, orient="index", columns=["chi5"])
chi_df = pd.concat([chi1_df, chi2_df, chi3_df, chi4_df, chi5_df], axis=1)
  
delta1_df = pd.DataFrame.from_dict(delta1, orient="index", columns=["delta1"])
delta2_df = pd.DataFrame.from_dict(delta2, orient="index", columns=["delta2"])
delta3_df = pd.DataFrame.from_dict(delta3, orient="index", columns=["delta3"])
delta4_df = pd.DataFrame.from_dict(delta4, orient="index", columns=["delta4"])
delta5_df = pd.DataFrame.from_dict(delta5, orient="index", columns=["delta5"])
delta_df = pd.concat([delta1_df, delta2_df, delta3_df, delta4_df, delta5_df], axis=1)      

# Name is assigned based on the options chosen
file_name = get_file_name("Simplified models coefficients - analytical.xlsx", exploration=exploration, success_rate=success_rate) 
    
with pd.ExcelWriter(os.path.join(absolute_path, "generated_files", file_name)) as writer:
        alpha_df.to_excel(writer, sheet_name='alpha')
        beta_df.to_excel(writer, sheet_name='beta')
        chi_df.to_excel(writer, sheet_name='chi')
        delta_df.to_excel(writer, sheet_name='delta')
    
    
