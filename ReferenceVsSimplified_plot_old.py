#%% Set up and load data
import brightway2 as bw
import seaborn as sb
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

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

#Retrive methods units
ILCD_units=[bw.methods[method]["unit"] for method in ILCD]

n_iter=10000
file_name= "ReferenceVsSimplified N" + str(n_iter)
ecoinvent_version = "ecoinvent_3.6"
folder_IN = os.path.join(absolute_path, "generated_files", ecoinvent_version, "validation")

cge_df = pd.read_json(os.path.join(folder_IN, file_name + " - Conventional"))
ege_df = pd.read_json(os.path.join(folder_IN, file_name + " - Enhanced"))

folder_OUT = os.path.join(absolute_path, "generated_plots", ecoinvent_version)

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

#%% Save boxplot
file_name_box = file_name + " Boxplot"

cge_boxplot.savefig(os.path.join(folder_OUT, file_name_box + " - Conventional.png"))
ege_boxplot.savefig(os.path.join(folder_OUT, file_name_box + " - Enhanced.png"))


#%% Violin plot 

cge_df_2=cge_df.melt(id_vars=["method_1", "method_2", "method_3"], var_name="model", value_name="score")
cge_violinplot = sb.catplot(data=cge_df_2, x="method_1", y="score", col="method_3", kind="violin", hue="model", col_wrap=4, split=False, sharex=False, sharey=False, legend=False)
for counter, ax in enumerate(cge_violinplot.axes.flatten()):
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    title_= ILCD[counter][2] + "\n" + "[" + ILCD_units[counter] + "]"
    ax.set(xlabel="", ylabel="",title=title_)
    ax.set_xticks([])
handles = cge_violinplot._legend_data.values()
labels = cge_violinplot._legend_data.keys()
cge_violinplot.fig.subplots_adjust(hspace = 0.4, wspace= 0.25, bottom=0.1, top=0.9)
lg_1 = cge_violinplot.fig.legend(handles=handles, labels=labels, loc='center', bbox_to_anchor=(0.1,0.97), ncol=2, borderaxespad=0.)

ege_df2=ege_df.melt(id_vars=["method_1", "method_2", "method_3"], var_name="model", value_name="score")
ege_violinplot = sb.catplot(data=ege_df2, x="method_1", y="score", col="method_3", kind="violin", hue="model", col_wrap=4, split=False, sharex=False, sharey=False, legend=False)
for counter, ax in enumerate(ege_violinplot.axes.flatten()):
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    title_= ILCD[counter][2] + "\n" + "[" + ILCD_units[counter] + "]"
    ax.set(xlabel="",ylabel="", title=title_)
    ax.set_xticks([])
handles = ege_violinplot._legend_data.values()
labels = ege_violinplot._legend_data.keys()
ege_violinplot.fig.subplots_adjust(hspace = 0.4, wspace= 0.25, bottom=0.1, top=0.9)
lg_2=ege_violinplot.fig.legend(handles=handles, labels=labels, loc='center', bbox_to_anchor=(0.1,0.97), ncol=2, borderaxespad=0.)

#%% 
cge_violinplot.fig.tight_layout(rect=[0,0,1,0.95])
ege_violinplot.fig.tight_layout(rect=[0,0,1,0.95])

#%% Save violinplot
file_name_box = file_name + " Violinplot"

cge_violinplot.savefig(os.path.join(folder_OUT, file_name_box + " - Conventional.png"), dpi=600)
ege_violinplot.savefig(os.path.join(folder_OUT, file_name_box + " - Enhanced.png"), dpi=600)

#%% Coefficient of determination

cge_r_squared = {}
cge_RMSE = {}
cge_mean = {}
for method in ILCD:
    df = cge_df[cge_df.method_3 == method[2]] 
    SS_Residual = sum(( df.Reference - df.Simplified ) **2 )
    SS_Total = sum(( df.Reference - df.Reference.mean() ) **2 )
    cge_r_squared[method] = [1 - (float(SS_Residual))/SS_Total]
    cge_RMSE[method] = [np.sqrt( SS_Residual/len(df.Reference) )]
    cge_mean[method] = df.Reference.mean()
    
ege_r_squared = {}
ege_RMSE = {}
ege_mean = {}
for method in ILCD:
    df = ege_df[ege_df.method_3 == method[2]] 
    SS_Residual = sum(( df.Reference - df.Simplified ) **2 )
    SS_Total = sum(( df.Reference - df.Reference.mean() ) **2 )
    ege_r_squared[method] = [1 - (float(SS_Residual))/SS_Total]
    ege_RMSE[method] = [np.sqrt( SS_Residual/len(df.Reference) )]
    ege_mean[method] = df.Reference.mean()
    

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
    x_lim = set_axlims (df.Reference, 0.15)
    y_lim = set_axlims (df.Simplified, 0.15)
    lim = ( 0 , max(x_lim[1], y_lim[1]) )
    sb.scatterplot(data=df, x="Reference", y="Simplified", s=5, alpha=0.3, linewidth=0)
    sb.lineplot(x=[0, 1e10], y=[0, 1e10], color="black", ax=ax_, linewidth=1)
    plt.xlim(lim)   
    plt.ylim(lim)
    ax_.ticklabel_format(style='sci', axis='both', scilimits=(0,0))
    title_= ILCD[i][2] + "\n" + "[" + ILCD_units[i] + "]"
    ax_.set(xlabel="", ylabel="", title=title_)
    tx = "$R^2$"+ ": " + str(round(cge_r_squared[method][0],2))
    ax_.text(0.05, 0.8, tx, transform=ax_.transAxes, fontsize=8)
    tx_2 = "RMSE: " + "{:.2e}".format(ege_RMSE[method][0])
    ax_.text(0.05, 0.7, tx_2, transform=ax_.transAxes, fontsize=8)
cge_parityplot.text(0.5, 0.01, 'General model', ha='center', fontsize=12, fontweight="bold")
cge_parityplot.text(0.01, 0.5, 'Simplified model', va='center', rotation='vertical', fontsize=12, fontweight="bold")  
  
# # Make figure full screen
# figManager = plt.get_current_fig_manager()
# figManager.window.showMaximized()
# #cge_parityplot.subplots_adjust(hspace = 0.9)

       
ege_parityplot=plt.figure()
for i, method in enumerate(ILCD):
    ax_=ege_parityplot.add_subplot(4,4,i+1)
    df = ege_df[ege_df.method_3 == method[2]]
    x_lim = set_axlims (df.Reference, 0.15)
    y_lim = set_axlims (df.Simplified, 0.15)
    lim = ( 0 , max(x_lim[1], y_lim[1]) )
    sb.scatterplot(data=df, x="Reference", y="Simplified", s=5, alpha=0.5, linewidth=0)
    sb.lineplot(x=[0, 1e10], y=[0, 1e10], color="black", ax=ax_, linewidth=1)
    plt.xlim(lim)   
    plt.ylim(lim)
    ax_.ticklabel_format(style='sci', axis='both', scilimits=(0,0))
    title_= ILCD[i][2] + "\n" + "[" + ILCD_units[i] + "]"
    ax_.set(xlabel="", ylabel="", title=title_)
    tx = "$R^2$"+ ": " +str(round(ege_r_squared[method][0],2))
    ax_.text(0.05, 0.8, tx, transform=ax_.transAxes, fontsize=8)
    tx_2 = "RMSE: " + "{:.2e}".format(ege_RMSE[method][0])
    ax_.text(0.05, 0.7, tx_2, transform=ax_.transAxes, fontsize=8)
ege_parityplot.text(0.5, 0.01, 'General model', ha='center', fontsize=12, fontweight="bold")
ege_parityplot.text(0.01, 0.5, 'Simplified model', va='center', rotation='vertical', fontsize=12, fontweight="bold")  
 
# # Make figure full screen
# figManager = plt.get_current_fig_manager()
# figManager.window.showMaximized()

#%% Plots sizes and layout
cge_parityplot.set_size_inches([14,  8])
ege_parityplot.set_size_inches([14,  8])
cge_parityplot.tight_layout(rect=[0.02,0.02,1,1])
ege_parityplot.tight_layout(rect=[0.02,0.02,1,1])

#%% Save figures

file_name_par = file_name + " Parity_Plot"
cge_parityplot.savefig(os.path.join(folder_OUT, file_name_par + " - Conventional.png"), dpi=600)
ege_parityplot.savefig(os.path.join(folder_OUT, file_name_par + " - Enhanced.png"), dpi=600)

#%% Save statisical measures

cge_r_squared_df = pd.DataFrame.from_dict(cge_r_squared, orient="index").reset_index()
ege_r_squared_df = pd.DataFrame.from_dict(ege_r_squared, orient="index").reset_index()
cge_RMSE_df = pd.DataFrame.from_dict(cge_RMSE, orient="index").reset_index()
ege_RMSE_df = pd.DataFrame.from_dict(ege_RMSE, orient="index").reset_index()
cge_mean_df = pd.DataFrame.from_dict(cge_mean, orient="index").reset_index()
ege_mean_df = pd.DataFrame.from_dict(ege_mean, orient="index").reset_index()

ILCD_df=pd.DataFrame(ILCD)
cge_stats_df=pd.concat([ILCD_df, cge_r_squared_df, cge_RMSE_df, cge_mean_df], axis=1).drop(columns="index")
ege_stats_df=pd.concat([ILCD_df, ege_r_squared_df, ege_RMSE_df, ege_mean_df], axis=1).drop(columns="index")
cge_stats_df.columns=["method_1", "method_2", "method_3", "R2", "RMSE", "mean_ref"]
ege_stats_df.columns=["method_1", "method_2", "method_3", "R2", "RMSE", "mean_ref"]

folder_OUT_2 = os.path.join(absolute_path, "generated_files", ecoinvent_version)
with pd.ExcelWriter(os.path.join(folder_OUT_2,'ReferenceVsSimplified statistics.xlsx')) as writer:  
    cge_stats_df.to_excel(writer, sheet_name='cge')
    ege_stats_df.to_excel(writer, sheet_name='ege')
    

#%% THIS IS TO MAKE POINTS COLOURED ACCORDING TO DENSITY

from scipy.stats import gaussian_kde as kde
from matplotlib.colors import Normalize
from matplotlib import cm
import numpy as np
import matplotlib.pyplot as plt

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
       

cge_parityplot_col=plt.figure()
for i, method in enumerate(ILCD):
    ax_=cge_parityplot_col.add_subplot(4,4,i+1)
    df = cge_df[cge_df.method_3 == method[2]]
    
    # Calculate kde density values
    df_ = df[["Reference", "Simplified"]].to_numpy().T
    kde_v= kde( df[["Reference", "Simplified"]].to_numpy().T ).evaluate(df_)
    
    # Sort kde value and df values by kde values
    kde_sort = kde_v.argsort()
    df_sort = df.iloc[kde_sort]
    kde_v_sort = kde_v[kde_sort]

    # Find axis limits
    x_lim = set_axlims (df.Reference, 0.02)
    y_lim = set_axlims (df.Simplified, 0.02)
    lim = ( 0 , max(x_lim[1], y_lim[1]) )
    
    # Parity plot
    sb.lineplot(x=[0, 1e10], y=[0, 1e10], color="black", ax=ax_, linewidth=1)
    plt.scatter(x=df_sort.Reference, y=df_sort.Simplified, s=7, c=kde_v_sort, cmap="cool", linewidth=0)
    
    # Add colorbar
    cbar=plt.colorbar()
    cbar.formatter.set_powerlimits((0,0))
    cbar.ax.yaxis.set_offset_position('left')
    cbar.set_label('KDE', rotation=270, labelpad=10)
    
    # Amend other features
    plt.xlim(lim)   
    plt.ylim(lim)
    ax_.ticklabel_format(style='sci', axis='both', scilimits=(0,0))
    title_= ILCD[i][2] + "\n" + "[" + ILCD_units[i] + "]"
    ax_.set(xlabel="", ylabel="", title=title_)
    tx = "$R^2$"+ ": " + str(round(cge_r_squared[method][0],2))
    ax_.text(0.05, 0.8, tx, transform=ax_.transAxes, fontsize=8)
    tx_2 = "RMSE: " + "{:.2e}".format(ege_RMSE[method][0])
    ax_.text(0.05, 0.7, tx_2, transform=ax_.transAxes, fontsize=8)   
cge_parityplot_col.text(0.5, 0.01, 'General model', ha='center', fontsize=12, fontweight="bold")
cge_parityplot_col.text(0.01, 0.5, 'Simplified model', va='center', rotation='vertical', fontsize=12, fontweight="bold")  
  
       
ege_parityplot_col=plt.figure()
for i, method in enumerate(ILCD):
    ax_=ege_parityplot_col.add_subplot(4,4,i+1)
    df = ege_df[ege_df.method_3 == method[2]]
    
    # Calculate kde density values
    df_ = df[["Reference", "Simplified"]].to_numpy().T
    kde_v= kde( df[["Reference", "Simplified"]].to_numpy().T ).evaluate(df_)
    
    # Sort kde value and df values by kde values
    kde_sort = kde_v.argsort()
    df_sort = df.iloc[kde_sort]
    kde_v_sort = kde_v[kde_sort]
    
    # Find axis limits
    x_lim = set_axlims (df.Reference, 0.02)
    y_lim = set_axlims (df.Simplified, 0.02)
    lim = ( 0 , max(x_lim[1], y_lim[1]) )
    
    #Parity plot
    sb.lineplot(x=[0, 1e10], y=[0, 1e10], color="black", ax=ax_, linewidth=1)
    plt.scatter(x=df_sort.Reference, y=df_sort.Simplified, s=7, c=kde_v_sort, cmap="copper_r", linewidth=0)
    plt.locator_params(axis='both', nbins=4)
    
    #Add color bar
    cbar=plt.colorbar()
    cbar.formatter.set_powerlimits((0,0))
    cbar.ax.yaxis.set_offset_position('left')
    cbar.set_label('KDE', rotation=270, labelpad=10)
    
    #Amend other features
    plt.xlim(lim)   
    plt.ylim(lim)
    ax_.ticklabel_format(style='sci', axis='both', scilimits=(0,0))
    title_= ILCD[i][2] + "\n" + "[" + ILCD_units[i] + "]"
    ax_.set(xlabel="", ylabel="", title=title_)
    tx = "$R^2$"+ ": " +str(round(ege_r_squared[method][0],2))
    ax_.text(0.05, 0.8, tx, transform=ax_.transAxes, fontsize=8)
    tx_2 = "RMSE: " + "{:.2e}".format(ege_RMSE[method][0])
    ax_.text(0.05, 0.7, tx_2, transform=ax_.transAxes, fontsize=8)
ege_parityplot_col.text(0.5, 0.01, 'General model', ha='center', fontsize=12, fontweight="bold")
ege_parityplot_col.text(0.01, 0.5, 'Simplified model', va='center', rotation='vertical', fontsize=12, fontweight="bold")  
 
cge_parityplot_col.subplots_adjust(wspace=0.1)
ege_parityplot_col.subplots_adjust(wspace=0.1)

cge_parityplot_col.set_size_inches([14,  8])
ege_parityplot_col.set_size_inches([14,  8])
cge_parityplot_col.tight_layout(rect=[0.02,0.02,1,1])
ege_parityplot_col.tight_layout(rect=[0.02,0.02,1,1])

#%% Save figures
file_name_par_col = file_name + " Parity_Plot_COL"
cge_parityplot_col.savefig(os.path.join(folder_OUT, file_name_par_col + " - Conventional.png"), dpi=600)
ege_parityplot_col.savefig(os.path.join(folder_OUT, file_name_par_col + " - Enhanced.png"), dpi=600)

