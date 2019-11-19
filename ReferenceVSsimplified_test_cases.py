#%% Set-up

import brightway2 as bw
import seaborn as sb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import warnings

# Set working directry
path = "."
os.chdir(path)

# Import local
#from cge_klausen import parameters as cge_parameters
#from ege_klausen import parameters as ege_parameters
from cge_model import GeothermalConventionalModel
from ege_model import GeothermalEnhancedModel
from s_models import simplified_cge_model, simplified_ege_model
from utils.lookup_func import lookup_geothermal
from utils.Stoc_MultiMethod_LCA_pygsa import run_mc

# Set project
bw.projects.set_current("Geothermal")

# Retrieve methods 

# List of methods is required for run_mc, but for initiating lca object we only need one element. Need to improve Stoc_Multimethod_LCA_pygsa
ILCD_CC = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)]

# Find demand
_, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_conv_prod, electricity_enh_prod = lookup_geothermal()

# Number of iterations
n_iter=100

# Load simplified models coefficients
absolute_path = os.path.abspath(path)
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

# Initiate lca object
lca = bw.LCA({electricity_conv_prod: 1}, ILCD_CC[0])

for p in cge_parameters: 
    p.stochastic(iterations=n_iter)  

    # Reference model
    cge_model = GeothermalConventionalModel(p)
    cge_parameters_sto=cge_model.run_ps(p)
    ref_cge = run_mc_2(cge_parameters_sto, electricity_conv_prod, ILCD_CC, n_iter)
    
    # TODO parameter passed to simplified_model needs to be a list! Need to change this.
    s_cge = simplified_cge_model(p, ILCD_CC[0], alpha, static=True)


####### UNDER DEVELOPMENT ############

#%% Conventional

# Generate stochastic values
cge_parameters.stochastic(iterations=n_iter)

# Initiate lca object
demand = {electricity_conv_prod: 1}
method = ILCD[0]
lca = bw.LCA(demand, method)
lca.lci()
lca.lcia()

# Reference model
cge_model = GeothermalConventionalModel(cge_parameters)
cge_parameters_sto=cge_model.run_ps(cge_parameters)
ref_cge = run_mc(n_iter, cge_parameters_sto, lca, ILCD)

# Simplified model
s_cge = {}
for method in ILCD:
    s_cge[method]=simplified_cge_model(cge_parameters, method, alpha, beta)

#%% Conventional plot    
ref_cge_df=pd.DataFrame.from_dict(ref_cge, orient="columns").melt(var_name=["method_1", "method_2", "method_3"],value_name="Reference")
#ref_cge_NR_df=pd.DataFrame.from_dict(ref_cge_NR, orient="columns").melt(var_name=["method_1", "method_2", "method_3"],value_name="Reference_NR")
s_cge_df=pd.DataFrame.from_dict(s_cge, orient="columns").melt(var_name=["method_1", "method_2", "method_3"], value_name="Simplified")

cge_df = pd.merge(ref_cge_df, s_cge_df["Simplified"], how="left", left_index=True, right_index=True)
#cge_df = pd.merge(cge_df, ref_cge_NR_df["Reference_NR"], how="left", left_index=True, right_index=True)
cge_df2=cge_df.melt(id_vars=["method_1", "method_2", "method_3"], var_name="model", value_name="score")

cge_plot = sb.catplot(data=cge_df2, x="model", y="score", col="method_3", kind="box", whis=[5,95], col_wrap=4, sharex=True, sharey=False, showfliers=False)

#%% Enhanced

# Generate stochastic values
ege_parameters.stochastic(iterations=n_iter)

# Initiate lca object
demand = {electricity_enh_prod: 1}
method = ILCD[0]
lca = bw.LCA(demand, method)
lca.lci()
lca.lcia()

# Reference model
ege_model = GeothermalEnhancedModel(ege_parameters)
ege_parameters_sto=ege_model.run_ps(ege_parameters)
ref_ege = run_mc(ege_parameters_sto, electricity_enh_prod, ILCD, n_iter)

# Simplified model
s_ege={}
for method in ILCD:
    s_ege[method]=simplified_ege_model(ege_parameters, method, chi, delta)
    
#%% Plot enhanced

ref_ege_df=pd.DataFrame.from_dict(ref_ege, orient="columns").melt(var_name=["method_1", "method_2", "method_3"],value_name="Reference")
ref_ege_NR_df=pd.DataFrame.from_dict(ref_ege_NR, orient="columns").melt(var_name=["method_1", "method_2", "method_3"],value_name="Reference_NR")
s_ege_df=pd.DataFrame.from_dict(s_ege, orient="columns").melt(var_name=["method_1", "method_2", "method_3"], value_name="Simplified")

ege_df = pd.merge(ref_ege_df, s_ege_df["Simplified"], how="left", left_index=True, right_index=True)
#ege_df = pd.merge(ege_df, ref_ege_NR_df["Reference_NR"], how="left", left_index=True, right_index=True)
ege_df2=ege_df.melt(id_vars=["method_1", "method_2", "method_3"], var_name="model", value_name="score")

ege_plot = sb.catplot(data=ege_df2, x="model", y="score", col="method_3", kind="box", whis=[5,95], col_wrap=4, sharex=True, sharey=False, showfliers=False)

#%% Coefficient of determination and scatter plot

p=2 # Number of parameters in simplified models except conventional - CC
cge_r_squared, cge_adjusted_r_squared = {}, {}
for method in ILCD:
    df = cge_df[cge_df.method_3 == method[2]] 
    SS_Residual = sum(( df.Reference - df.Simplified ) **2 )
    SS_Total = sum(( df.Reference - df.Reference.mean() ) **2 )
    cge_r_squared[method] = 1 - (float(SS_Residual))/SS_Total
    if method != ILCD_CC[0]:
        cge_adjusted_r_squared[method] = 1 - (1-cge_r_squared[method]) * (n_iter-1)/(p-1)

ege_r_squared, ege_adjusted_r_squared = {}, {}
for method in ILCD:
    df = ege_df[ege_df.method_3 == method[2]] 
    SS_Residual = sum(( df.Reference - df.Simplified ) **2 )
    SS_Total = sum(( df.Reference - df.Reference.mean() ) **2 )
    ege_r_squared[method] = 1 - (float(SS_Residual))/SS_Total
    if method != ILCD_CC[0]:
        ege_adjusted_r_squared[method] = 1 - (1-ege_r_squared[method])* (n_iter-1)/(p-1)

end_time=time.time()
print("Total time: ", end_time-start_time)


# TODO Categorical plot doesn't work for unknown reasons.
# cge_sc_plot = sb.catplot(data=cge_df, x="Reference", y="Simplified", col="method_3", kind="strip", jitter=False, col_wrap=4, sharex=False, sharey=False)
# sb.lineplot(data=cge_df, x="Reference", y="Reference", col="method_3", color="black")

# ege_sc_plot = sb.catplot(data=ege_df, x="Reference", y="Simplified", col="method_3", kind="strip", jitter=False, col_wrap=4, sharex=False, sharey=False)
# sb.lineplot(data=ege_df, x="Reference", y="Reference", col="method_3", color="black")

# Plotting with with Seaborn and for cycle

def set_axlims(series, marginfactor):
    """
    Fix for a scaling issue with matplotlibs scatterplot and small values.
    Takes in a pandas series, and a marginfactor (float).
    A marginfactor of 0.2 would for example set a 20% border distance on both sides.
    Output:[bottom,top]
    To be used with .set_ylim(bottom,top)
    """
    minv = series.min()
    maxv = series.max()
    datarange = maxv-minv
    border = abs(datarange*marginfactor)
    maxlim = maxv+border
    minlim = minv-border

    return minlim,maxlim

fig=plt.figure()

for i, method in enumerate(ILCD):
    fig.add_subplot(4,4,i+1)
    df = cge_df[cge_df.method_3 == method[2]]
    x_lim = set_axlims (df.Reference, 0.3)
    y_lim = set_axlims (df.Simplified, 0.3)
    lim = ( 0 , max(x_lim[1], y_lim[1]) )
    sb.scatterplot(data=df, x="Reference", y="Simplified").set_title(method[2])
    sb.lineplot(x=[0, 1e10], y=[0, 1e10], color="black")
    plt.xlim(lim)   
    plt.ylim(lim)          


#%% Printing stuff
par = {}

for k in cge_parameters.keys():
    par[k] = cge_parameters[k]
    
par_df = pd.DataFrame.from_dict(par)

par_sto = {}
for i in range(len(cge_parameters_sto)):
    name= bw.get_activity(cge_parameters_sto[i][0])
    par_sto[name] = cge_parameters_sto[i][2]
    
par_sto_df = pd.DataFrame.from_dict(par_sto)

par_df.to_excel("par_df.xlsx")
par_sto_df.to_excel("par_sto_df.xlsx")

# Plot with Matplotlib only
#fig, ax = plt.subplots(4, 4)
#j=0
#k=0
#
#for i, method in enumerate(ILCD):
#    df = cge_df[cge_df.method_3 == method[2]]
#    ax[k,j].scatter(x=df.Reference, y=df.Simplified)
#    if j==3:
#        j=0
#        k+=1
#    else:
#        j+=1
        
# Used to checlk r squared 
#from sklearn.metrics import r2_score
#
#cge_r_squared_SK={}
#for method in ILCD:
#    df = cge_df[cge_df.method_3 == method[2]] 
#    cge_r_squared_SK[method]=r2_score(df.Reference, df.Simplified)
