#%% Set up and load data
import brightway2 as bw
import seaborn as sb
import matplotlib.pyplot as plt
import pandas as pd
import os

# Set working directry
path = "."
os.chdir(path)
absolute_path = os.path.abspath(path)

# Set project
bw.projects.set_current("Geothermal")

# Retrieve methods 
ILCD_CC = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)]
ILCD_HH = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "human health" in str(method)]
ILCD_EQ = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "ecosystem quality" in str(method)]
ILCD_RE = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "resources" in str(method)]
ILCD = ILCD_CC + ILCD_HH + ILCD_EQ + ILCD_RE

cge_df = pd.read_json(os.path.join(absolute_path, "generated_files/Conventional ReferenceVsSimplified N10000"))
ege_df = pd.read_json(os.path.join(absolute_path, "generated_files/Enhanced ReferenceVsSimplified N10000"))

#%% Box plot

cge_df_2=cge_df.melt(id_vars=["method_1", "method_2", "method_3"], var_name="model", value_name="score")
cge_boxplot = sb.catplot(data=cge_df_2, x="model", y="score", col="method_3", kind="box", whis=[5,95], col_wrap=4, sharex=True, sharey=False, showfliers=False)

ege_df2=ege_df.melt(id_vars=["method_1", "method_2", "method_3"], var_name="model", value_name="score")
ege_boxplot = sb.catplot(data=ege_df2, x="model", y="score", col="method_3", kind="box", whis=[5,95], col_wrap=4, sharex=True, sharey=False, showfliers=False)

#%% Coefficient of determination

cge_r_squared = {}
for method in ILCD:
    df = cge_df[cge_df.method_3 == method[2]] 
    SS_Residual = sum(( df.Reference - df.Simplified ) **2 )
    SS_Total = sum(( df.Reference - df.Reference.mean() ) **2 )
    cge_r_squared[method] = 1 - (float(SS_Residual))/SS_Total
    
ege_r_squared = {}
for method in ILCD:
    df = ege_df[ege_df.method_3 == method[2]] 
    SS_Residual = sum(( df.Reference - df.Simplified ) **2 )
    SS_Total = sum(( df.Reference - df.Reference.mean() ) **2 )
    ege_r_squared[method] = 1 - (float(SS_Residual))/SS_Total
    

#%% Parity plot

# Plotting with with Matplotlib and seaborn

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


# TODO Need to fix axis labels and include R squared as text in the graphs
    
cge_parityplot=plt.figure()

for i, method in enumerate(ILCD):
    cge_parityplot.add_subplot(4,4,i+1)
    df = cge_df[cge_df.method_3 == method[2]]
    x_lim = set_axlims (df.Reference, 0.3)
    y_lim = set_axlims (df.Simplified, 0.3)
    lim = ( 0 , max(x_lim[1], y_lim[1]) )
    sb.scatterplot(data=df, x="Reference", y="Simplified").set_title(method[2])
    sb.lineplot(x=[0, 1e10], y=[0, 1e10], color="black")
    plt.xlim(lim)   
    plt.ylim(lim) 
        
cge_parityplot=plt.figure()

for i, method in enumerate(ILCD):
    ege_parityplot.add_subplot(4,4,i+1)
    df = ege_df[ege_df.method_3 == method[2]]
    x_lim = set_axlims (df.Reference, 0.3)
    y_lim = set_axlims (df.Simplified, 0.3)
    lim = ( 0 , max(x_lim[1], y_lim[1]) )
    sb.scatterplot(data=df, x="Reference", y="Simplified").set_title(method[2])
    sb.lineplot(x=[0, 1e10], y=[0, 1e10], color="black")
    plt.xlim(lim)   
    plt.ylim(lim)   
    
# TODO Seabon categorical plot doesn't work for unknown reasons.
# cge_sc_plot = sb.catplot(data=cge_df, x="Reference", y="Simplified", col="method_3", kind="strip", jitter=False, col_wrap=4, sharex=False, sharey=False)
# sb.lineplot(data=cge_df, x="Reference", y="Reference", col="method_3", color="black")
# ege_sc_plot = sb.catplot(data=ege_df, x="Reference", y="Simplified", col="method_3", kind="strip", jitter=False, col_wrap=4, sharex=False, sharey=False)
# sb.lineplot(data=ege_df, x="Reference", y="Reference", col="method_3", color="black")