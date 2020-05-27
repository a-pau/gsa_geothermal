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
ILCD_CC, ILCD_CC_units = get_ILCD_methods(units=True, CC_only=True)

# Upload
n_iter=10000
threshold_cge = 0.15
threshold_ege = 0.15

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


#%% Parity plot coloured according to density

from scipy.stats import gaussian_kde as kde
from matplotlib.colors import Normalize
from matplotlib import cm
from utils.plot_funcs import set_axlims 
from scipy.stats import spearmanr, pearsonr      

#%% Conventional

cge_parityplot_col=plt.figure()

df = cge_df[cge_df.method == ILCD_CC[0][2]]

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
ax_=sb.lineplot(x=[0, 1e10], y=[0, 1e10], color="black",  linewidth=1)
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
ax_.set_title(label="Climate change [kg CO2-eq.] \n", fontsize=11)
ax_.set(xlabel="General model", ylabel="Simplified model")  

# Calculate Pearson and Spearman
cge_sp = spearmanr(df["Reference"], df["Simplified"])[0]
cge_pe = pearsonr(df["Reference"], df["Simplified"])[0]

#Add text
tx = "Pearson: " + str(round(cge_pe,2))
ax_.text(0.05, 0.9, tx, transform=ax_.transAxes, fontsize=9)
tx_2 = "Spearman: " +  str(round(cge_sp,2))
ax_.text(0.05, 0.85, tx_2, transform=ax_.transAxes, fontsize=9)

#cge_parityplot_col.suptitle("CONVENTIONAL, THRESHOLD="+"{:.0%}".format(threshold_cge))


#%% Enhanced     
ege_parityplot_col=plt.figure()

df = ege_df[ege_df.method == ILCD_CC[0][2]]

# Remove outliers
qt = 0.999 
qt_val = df.Reference.quantile(qt)
df=df[df.Reference<qt_val]
   
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
ax_=sb.lineplot(x=[0, 1e10], y=[0, 1e10], color="black", linewidth=1)
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
ax_.set_title(label="Climate change [kg CO2-eq.] \n", fontsize=11)
ax_.set(xlabel="General model", ylabel="Simplified model")

# Calculate Pearson and Spearman
ege_sp = spearmanr(df["Reference"], df["Simplified"])[0]
ege_pe = pearsonr(df["Reference"], df["Simplified"])[0]

#Add text
tx = "Pearson: " + str(round(ege_pe,2))
ax_.text(0.05, 0.9, tx, transform=ax_.transAxes, fontsize=9)
tx_2 = "Spearman: " +  str(round(ege_sp,2))
ax_.text(0.05, 0.85, tx_2, transform=ax_.transAxes, fontsize=9)

#ege_parityplot_col.suptitle("ENHANCED, THRESHOLD="+"{:.0%}".format(threshold_ege))


#%% Save figures
file_name_par_col = file_name + " Parity_Plot_COL_Goldschmidt"
cge_parityplot_col.savefig(os.path.join(folder_OUT, file_name_par_col + "_Conventional_t"+str(threshold_cge)+".png"), dpi=300)
ege_parityplot_col.savefig(os.path.join(folder_OUT, file_name_par_col + "_Enhanced_t"+str(threshold_cge)+".png"), dpi=300)
