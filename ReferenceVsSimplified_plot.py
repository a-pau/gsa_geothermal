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

n_iter=10000
file_name= "ReferenceVsSimplified N" + str(n_iter)
ecoinvent_version = "ecoinvent_3.6"
folder_IN = os.path.join(absolute_path, "generated_files", ecoinvent_version, "validation")

cge_df = pd.read_json(os.path.join(folder_IN, file_name + " - Conventional"))
ege_df = pd.read_json(os.path.join(folder_IN, file_name + " - Enhanced"))

#%% Box plot

cge_df_2=cge_df.melt(id_vars=["method_1", "method_2", "method_3"], var_name="model", value_name="score")
cge_boxplot = sb.catplot(data=cge_df_2, x="model", y="score", col="method_3", kind="box", whis=[5,95], col_wrap=4, sharex=True, sharey=False, showfliers=False, height=4)
for counter, ax in enumerate(cge_boxplot.axes.flatten()):
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    ax.set(xlabel="", title=ILCD[counter][2])
#cge_boxplot.fig.tight_layout()
cge_boxplot.fig.subplots_adjust(hspace = 0.3, wspace= 0.25, top=0.95)

ege_df2=ege_df.melt(id_vars=["method_1", "method_2", "method_3"], var_name="model", value_name="score")
ege_boxplot = sb.catplot(data=ege_df2, x="model", y="score", col="method_3", kind="box", whis=[5,95], col_wrap=4, sharex=True, sharey=False, showfliers=False)
for counter, ax in enumerate(ege_boxplot.axes.flatten()):
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    ax.set(xlabel="", title=ILCD[counter][2])
ege_boxplot.fig.subplots_adjust(hspace = 0.3, wspace= 0.25, top=0.95)

#%% First make plot full screen
#cge_boxplot.tight_layout()
#ege_boxplot.tight_layout()

#%% Save boxlot
file_name_box = file_name + " Boxplot"
folder_OUT = os.path.join(absolute_path, "generated_plots", ecoinvent_version)

cge_boxplot.savefig(os.path.join(folder_OUT, file_name_box + " - Conventional.png"))
ege_boxplot.savefig(os.path.join(folder_OUT, file_name_box + " - Enhanced.png"))

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
  
cge_parityplot=plt.figure()
for i, method in enumerate(ILCD):
    ax_=cge_parityplot.add_subplot(4,4,i+1)
    df = cge_df[cge_df.method_3 == method[2]]
    x_lim = set_axlims (df.Reference, 0.3)
    y_lim = set_axlims (df.Simplified, 0.3)
    lim = ( 0 , max(x_lim[1], y_lim[1]) )
    sb.scatterplot(data=df, x="Reference", y="Simplified")
    sb.lineplot(x=[0, 1e10], y=[0, 1e10], color="black", ax=ax_)
    plt.xlim(lim)   
    plt.ylim(lim)
    ax_.ticklabel_format(style='sci', axis='both', scilimits=(0,0))
    ax_.set(xlabel="", ylabel="", title=method[2] + "\n")
    tx = "$R^2$"+ ": " +str(round(cge_r_squared[method],3))
    ax_.text(0.5, 0.8, tx, transform=ax_.transAxes)
# Make figure full screen
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()
#cge_parityplot.subplots_adjust(hspace = 0.9)

       
ege_parityplot=plt.figure()
for i, method in enumerate(ILCD):
    ax_=ege_parityplot.add_subplot(4,4,i+1)
    df = ege_df[ege_df.method_3 == method[2]]
    x_lim = set_axlims (df.Reference, 0.3)
    y_lim = set_axlims (df.Simplified, 0.3)
    lim = ( 0 , max(x_lim[1], y_lim[1]) )
    sb.scatterplot(data=df, x="Reference", y="Simplified")
    sb.lineplot(x=[0, 1e10], y=[0, 1e10], color="black")
    plt.xlim(lim)   
    plt.ylim(lim)
    ax_.ticklabel_format(style='sci', axis='both', scilimits=(0,0))
    ax_.set(xlabel="", ylabel="", title=method[2] + "\n")
    tx = "$R^2$"+ ": " +str(round(ege_r_squared[method],3))
    ax_.text(0.5, 0.8, tx, transform=ax_.transAxes)
# Make figure full screen
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()

#%% First make plot full screen
cge_parityplot.tight_layout()
ege_parityplot.tight_layout()

#%% Save figures

file_name_par = file_name + " Parity_Plot"
cge_parityplot.savefig(os.path.join(folder_OUT, file_name_par + " - Conventional.png"))
ege_parityplot.savefig(os.path.join(folder_OUT, file_name_par + " - Enhanced.png"))

#%%   
# TODO Seabon categorical plot doesn't work for unknown reasons.
# cge_sc_plot = sb.catplot(data=cge_df, x="Reference", y="Simplified", col="method_3", kind="strip", jitter=False, col_wrap=4, sharex=False, sharey=False)
# sb.lineplot(data=cge_df, x="Reference", y="Reference", col="method_3", color="black")
# ege_sc_plot = sb.catplot(data=ege_df, x="Reference", y="Simplified", col="method_3", kind="strip", jitter=False, col_wrap=4, sharex=False, sharey=False)
# sb.lineplot(data=ege_df, x="Reference", y="Reference", col="method_3", color="black")