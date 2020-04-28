#%% Set up and load data
import brightway2 as bw
import seaborn as sb
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

# Import local
from setup_files_gsa import get_ILCD_methods

# Set working directry
path = "."
os.chdir(path)
absolute_path = os.path.abspath(path)

# Set project
bw.projects.set_current("Geothermal")

# Methods
ILCD, ILCD_units = get_ILCD_methods(units=True)

# Upload
n_iter=10000
threshold_cge = 0.05
threshold_ege = 0.05

ecoinvent_version = "ecoinvent_3.6"
folder_IN = os.path.join(absolute_path, "generated_files", ecoinvent_version, "validation")
file_name= "ReferenceVsSimplified_N" + str(n_iter)

cge_ref_df = pd.read_json(os.path.join(folder_IN, file_name + "_Conventional_Reference")).melt(var_name="method", value_name="Reference")
cge_s_df = pd.read_json(os.path.join(folder_IN, file_name + "_Conventional_Simplified_t"+str(threshold_cge))).melt(var_name="method", value_name="Simplified")
cge_df = pd.concat([cge_ref_df, cge_s_df["Simplified"]], axis=1)

ege_ref_df = pd.read_json(os.path.join(folder_IN, file_name + "_Enhanced_Reference")).melt(var_name="method", value_name="Reference")
ege_s_df = pd.read_json(os.path.join(folder_IN, file_name + "_Enhanced_Simplified_t"+str(threshold_ege))).melt(var_name="method", value_name="Simplified")
ege_df = pd.concat([ege_ref_df, ege_s_df["Simplified"]], axis=1)

folder_OUT = os.path.join(absolute_path, "generated_plots", ecoinvent_version)

#%% Box plot

# Re-arrange dataframe
cge_df_2=cge_df.melt(id_vars="method", var_name="model", value_name="score")

cge_boxplot = sb.catplot(data=cge_df_2, x="model", y="score", col="method", kind="box", whis=[5,95], col_wrap=4, sharex=True, sharey=False, showfliers=False, height=4)
for counter, ax in enumerate(cge_boxplot.axes.flatten()):
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    ax.set(xlabel="", title=ILCD[counter][2])
#cge_boxplot.fig.tight_layout()
cge_boxplot.fig.subplots_adjust(hspace = 0.3, wspace= 0.25, top=0.90)
cge_boxplot.fig.suptitle("CONVENTIONAL - THRESHOLD " + str(threshold_cge), size=12)


ege_df2=ege_df.melt(id_vars="method", var_name="model", value_name="score")
ege_boxplot = sb.catplot(data=ege_df2, x="model", y="score", col="method", kind="box", whis=[5,95], col_wrap=4, sharex=True, sharey=False, showfliers=False)
for counter, ax in enumerate(ege_boxplot.axes.flatten()):
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    ax.set(xlabel="", title=ILCD[counter][2])
ege_boxplot.fig.subplots_adjust(hspace = 0.3, wspace= 0.25, top=0.90)
ege_boxplot.fig.suptitle("ENHANCED - THRESHOLD " + str(threshold_ege), size=12)

#%% Save boxplot
file_name_box = file_name + " Boxplot"

cge_boxplot.savefig(os.path.join(folder_OUT, file_name_box + "_Conventional_t"+str(threshold_cge)".png"))
ege_boxplot.savefig(os.path.join(folder_OUT, file_name_box + "_Enhanced_t"+str(threshold_ege)".png"))


#%% Violin plot 

cge_df_3=cge_df.melt(id_vars="method", var_name="model", value_name="score")
cge_df_3["temp"] = "temp"

cge_violinplot = sb.catplot(data=cge_df_3, x="temp", y="score", col="method", kind="violin", hue="model", col_wrap=4, split=False, sharex=False, sharey=False, legend=False)
for counter, ax in enumerate(cge_violinplot.axes.flatten()):
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    title_= ILCD[counter][2] + "\n" + "[" + ILCD_units[counter] + "]"
    ax.set(xlabel="", ylabel="",title=title_)
    ax.set_xticks([])
handles = cge_violinplot._legend_data.values()
labels = cge_violinplot._legend_data.keys()
cge_violinplot.fig.subplots_adjust(hspace = 0.4, wspace= 0.25, bottom=0.1, top=0.9)
lg_1 = cge_violinplot.fig.legend(handles=handles, labels=labels, loc='center', bbox_to_anchor=(0.5,0.97), ncol=2, borderaxespad=0.)

ege_df_3=ege_df.melt(id_vars="method", var_name="model", value_name="score")
ege_df_3["temp"] = "temp"

ege_violinplot = sb.catplot(data=ege_df_3, x="temp", y="score", col="method", kind="violin", hue="model", col_wrap=4, split=False, sharex=False, sharey=False, legend=False)
for counter, ax in enumerate(ege_violinplot.axes.flatten()):
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    title_= ILCD[counter][2] + "\n" + "[" + ILCD_units[counter] + "]"
    ax.set(xlabel="",ylabel="", title=title_)
    ax.set_xticks([])
handles = ege_violinplot._legend_data.values()
labels = ege_violinplot._legend_data.keys()
ege_violinplot.fig.subplots_adjust(hspace = 0.4, wspace= 0.25, bottom=0.1, top=0.9)
lg_2=ege_violinplot.fig.legend(handles=handles, labels=labels, loc='center', bbox_to_anchor=(0.5,0.97), ncol=2, borderaxespad=0.)

#%% 
cge_violinplot.fig.tight_layout(rect=[0,0,1,0.95])
ege_violinplot.fig.tight_layout(rect=[0,0,1,0.95])

#%% Save violinplot
file_name_box = file_name + " Violinplot"

cge_violinplot.savefig(os.path.join(folder_OUT, file_name_box + "_Conventional_t"+str(threshold_cge)".png"), dpi=600)
ege_violinplot.savefig(os.path.join(folder_OUT, file_name_box + "_Enhanced_t"+str(threshold_ege)".png"), dpi=600)

#%% Parity plot coloured according to density

from scipy.stats import gaussian_kde as kde
from matplotlib.colors import Normalize
from matplotlib import cm
from utils.plot_funcs import set_axlims       

cge_parityplot_col=plt.figure()
for i, method in enumerate(ILCD):
    ax_=cge_parityplot_col.add_subplot(4,4,i+1)
    df = cge_df[cge_df.method == method[2]]
    
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
    ax_.set_title(label=title_, fontsize=9)
    ax_.set(xlabel="", ylabel="")  
cge_parityplot_col.text(0.5, 0.01, 'General model', ha='center', fontsize=12, fontweight="bold")
cge_parityplot_col.text(0.01, 0.5, 'Simplified model', va='center', rotation='vertical', fontsize=12, fontweight="bold")  

       
ege_parityplot_col=plt.figure()
for i, method in enumerate(ILCD):
    ax_=ege_parityplot_col.add_subplot(4,4,i+1)
    df = ege_df[ege_df.method == method[2]]
    
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
    plt.scatter(x=df_sort.Reference, y=df_sort.Simplified, s=7, c=kde_v_sort, cmap="cool", linewidth=0)
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
    ax_.set_title(label=title_, fontsize=9)
    ax_.set(xlabel="", ylabel="")
ege_parityplot_col.text(0.5, 0.01, 'General model', ha='center', fontsize=12, fontweight="bold")
ege_parityplot_col.text(0.01, 0.5, 'Simplified model', va='center', rotation='vertical', fontsize=12, fontweight="bold")  

cge_parityplot_col.suptitle("CONVENTIONAL, THRESHOLD="+"{:.0%}".format(threshold_cge))
ege_parityplot_col.suptitle("ENHANCED, THRESHOLD="+"{:.0%}".format(threshold_ege))

cge_parityplot_col.set_size_inches([13,  13])
ege_parityplot_col.set_size_inches([13,  13])
cge_parityplot_col.tight_layout(rect=[0.02,0.02,1,0.95])
ege_parityplot_col.tight_layout(rect=[0.02,0.02,1,0.95])

#cge_parityplot_col.subplots_adjust(wspace=0.1, hspace=0.6)
#ege_parityplot_col.subplots_adjust(wspace=0.1, hspace=0.6)

#%% Save figures
file_name_par_col = file_name + " Parity_Plot_COL"
cge_parityplot_col.savefig(os.path.join(folder_OUT, file_name_par_col + "_Conventional_t"+str(threshold_cge)+".tiff"), dpi=300)
ege_parityplot_col.savefig(os.path.join(folder_OUT, file_name_par_col + "_Enhanced_t"+str(threshold_cge)+".tiff"), dpi=300)

#%% Parity plot not coloured according to density

# from utils.plot_funcs import set_axlims

# # Plotting with with Matplotlib and seaborn
  
# cge_parityplot=plt.figure()
# for i, method in enumerate(ILCD):
#     ax_=cge_parityplot.add_subplot(4,4,i+1)
#     df = cge_df[cge_df.method == method[2]]
#     x_lim = set_axlims (df.Reference, 0.15)
#     y_lim = set_axlims (df.Simplified, 0.15)
#     lim = ( 0 , max(x_lim[1], y_lim[1]) )
#     sb.scatterplot(data=df, x="Reference", y="Simplified", s=5, alpha=0.3, linewidth=0)
#     sb.lineplot(x=[0, 1e10], y=[0, 1e10], color="black", ax=ax_, linewidth=1)
#     plt.xlim(lim)   
#     plt.ylim(lim)
#     ax_.ticklabel_format(style='sci', axis='both', scilimits=(0,0))
#     title_= ILCD[i][2] + "\n" + "[" + ILCD_units[i] + "]"
#     ax_.set(xlabel="", ylabel="", title=title_)
#     tx = "$R^2$"+ ": " + str(round(cge_r_squared[method][0],2))
#     ax_.text(0.05, 0.8, tx, transform=ax_.transAxes, fontsize=8)
#     tx_2 = "RMSE: " + "{:.2e}".format(cge_RMSE[method][0])
#     ax_.text(0.05, 0.7, tx_2, transform=ax_.transAxes, fontsize=8)
# cge_parityplot.text(0.5, 0.01, 'General model', ha='center', fontsize=12, fontweight="bold")
# cge_parityplot.text(0.01, 0.5, 'Simplified model', va='center', rotation='vertical', fontsize=12, fontweight="bold")  
  
       
# ege_parityplot=plt.figure()
# for i, method in enumerate(ILCD):
#     ax_=ege_parityplot.add_subplot(4,4,i+1)
#     df = ege_df[ege_df.method == method[2]]
#     x_lim = set_axlims (df.Reference, 0.15)
#     y_lim = set_axlims (df.Simplified, 0.15)
#     lim = ( 0 , max(x_lim[1], y_lim[1]) )
#     sb.scatterplot(data=df, x="Reference", y="Simplified", s=5, alpha=0.5, linewidth=0)
#     sb.lineplot(x=[0, 1e10], y=[0, 1e10], color="black", ax=ax_, linewidth=1)
#     plt.xlim(lim)   
#     plt.ylim(lim)
#     ax_.ticklabel_format(style='sci', axis='both', scilimits=(0,0))
#     title_= ILCD[i][2] + "\n" + "[" + ILCD_units[i] + "]"
#     ax_.set(xlabel="", ylabel="", title=title_)
#     tx = "$R^2$"+ ": " +str(round(ege_r_squared[method][0],2))
#     ax_.text(0.05, 0.8, tx, transform=ax_.transAxes, fontsize=8)
#     tx_2 = "RMSE: " + "{:.2e}".format(ege_RMSE[method][0])
#     ax_.text(0.05, 0.7, tx_2, transform=ax_.transAxes, fontsize=8)
# ege_parityplot.text(0.5, 0.01, 'General model', ha='center', fontsize=12, fontweight="bold")
# ege_parityplot.text(0.01, 0.5, 'Simplified model', va='center', rotation='vertical', fontsize=12, fontweight="bold")  
 
# # Plots sizes and layout
# cge_parityplot.set_size_inches([14,  8])
# ege_parityplot.set_size_inches([14,  8])
# cge_parityplot.tight_layout(rect=[0.02,0.02,1,1])
# ege_parityplot.tight_layout(rect=[0.02,0.02,1,1])

# #%% Save figures

# file_name_par = file_name + " Parity_Plot"
# cge_parityplot.savefig(os.path.join(folder_OUT, file_name_par + "_Conventional_t"+str(threshold_cge)".png"), dpi=600)
# ege_parityplot.savefig(os.path.join(folder_OUT, file_name_par + "_Enhanced_t"+str(threshold_ege)".png"), dpi=600)  

