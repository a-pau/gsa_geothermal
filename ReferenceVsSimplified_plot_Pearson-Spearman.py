#%% Set up and load data
import brightway2 as bw
import seaborn as sb
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from scipy.stats import spearmanr, pearsonr
from matplotlib import ticker

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

# Iterations
n_iter=10000

# Folders
file_name= "ReferenceVsSimplified_N" + str(n_iter)
ecoinvent_version = "ecoinvent_3.6"
folder_IN = os.path.join(absolute_path, "generated_files", ecoinvent_version, "validation")
folder_OUT = os.path.join(absolute_path, "generated_plots", ecoinvent_version)

# Thresholds
threshold = [0.2, 0.15, 0.1, 0.05]

# Reference
cge_ref_df = pd.read_json(os.path.join(folder_IN, file_name + "_Conventional_Reference")).melt(var_name="method", value_name="Reference")
ege_ref_df = pd.read_json(os.path.join(folder_IN, file_name + "_Enhanced_Reference")).melt(var_name="method", value_name="Reference")

cge_s_df = {}
ege_s_df = {}
for t in threshold:
    cge_s_df[t] = pd.read_json(os.path.join(folder_IN, file_name + "_Conventional_Simplified_t"+str(t))).melt(var_name="method", value_name="Simplified_"+str(t))
    ege_s_df[t] = pd.read_json(os.path.join(folder_IN, file_name + "_Enhanced_Simplified_t"+str(t))).melt(var_name="method", value_name="Simplified_"+str(t))

cge_df = cge_ref_df
ege_df = ege_ref_df
for t in threshold:
    cge_df = pd.concat([cge_df, cge_s_df[t]["Simplified_"+str(t)]], axis=1)
    ege_df = pd.concat([ege_df, ege_s_df[t]["Simplified_"+str(t)]], axis=1)

#%% Calculate spearman and pearson correlation coefficient

cge_pearson, cge_spearman = {}, {}
for method in ILCD:
    df = cge_df[cge_df.method == method[2]]
    sp_={}
    pe_={}
    for t in threshold:
        sp_[t] = spearmanr(df["Reference"], df["Simplified_"+str(t)])[0]
        pe_[t] = pearsonr(df["Reference"], df["Simplified_"+str(t)])[0]
        cge_spearman[method[2]] = sp_
        cge_pearson[method[2]] = pe_

cge_pearson_df = pd.DataFrame.from_dict(cge_pearson, orient="index")
cge_pearson_df.columns = ["{:.0%}".format(t) for t in cge_pearson_df.columns]
cge_spearman_df = pd.DataFrame.from_dict(cge_spearman, orient="index")
cge_spearman_df.columns = ["{:.0%}".format(t) for t in cge_spearman_df.columns]

# Remove outliers
qt = 0.999 
ege_pearson, ege_spearman = {}, {}
for method in ILCD:
    df = ege_df[ege_df.method == method[2]]
    sp_={}
    pe_={}
    for t in threshold:
        qt_val = df.Reference.quantile(qt)
        mask = np.where(df.Reference<qt_val, True, False)
        sp_[t] = spearmanr(df["Reference"][mask], df["Simplified_"+str(t)][mask])[0]
        pe_[t] = pearsonr(df["Reference"][mask], df["Simplified_"+str(t)][mask])[0]
        ege_spearman[method[2]] = sp_
        ege_pearson[method[2]] = pe_

ege_pearson_df = pd.DataFrame.from_dict(ege_pearson, orient="index")
ege_pearson_df.columns = ["{:.0%}".format(t) for t in ege_pearson_df.columns]
ege_spearman_df = pd.DataFrame.from_dict(ege_spearman, orient="index")
ege_spearman_df.columns = ["{:.0%}".format(t) for t in ege_spearman_df.columns]

#%% Plot Pearson

# Re arrange dataframes
cge_pearson_df_m = cge_pearson_df.reset_index().rename(columns={"index":"method"})
cge_pearson_df_m = cge_pearson_df_m.melt(id_vars="method",var_name="threshold", value_name="pearson")
ege_pearson_df_m = ege_pearson_df.reset_index().rename(columns={"index":"method"})
ege_pearson_df_m = ege_pearson_df_m.melt(id_vars="method",var_name="threshold", value_name="pearson")

# Set seaborn style
sb.set_style("darkgrid")
sb.set_context(rc={"axes.titlesize":12,"axes.labelsize":11, 
                   "xtick.labelsize":10, "ytick.labelsize":10, "legend.fontsize":10})

# Subplots
fig_pears, (cge_pears_ax, ege_pears_ax) = plt.subplots(nrows=1, ncols=2, sharey=True)

# Enable minor ticks
plt.minorticks_on()

#Set xticks
xticks=[0.8,0.85,0.9,0.95,1]

# CONVENTIONAL
#Plot
sb.stripplot(data=cge_pearson_df_m, y="method", x="pearson", hue="threshold", dodge=True, s=6,
             ax=cge_pears_ax)
cge_pears_ax.set(xlim=(0.8,1.01), xlabel="r", ylabel="", title="CONVENTIONAL", xticks=xticks)
cge_pears_ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
cge_pears_ax.grid(which='minor', axis='y')
cge_pears_ax.get_legend().remove()

# ENHANCED
#Plot
sb.stripplot(data=ege_pearson_df_m, y="method", x="pearson", hue="threshold", dodge=True, s=6,
             ax=ege_pears_ax)
ege_pears_ax.set(xlim=(0.8,1.01), xlabel="r", ylabel="", title="ENHANCED", xticks=xticks)
ege_pears_ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
ege_pears_ax.grid(which='minor', axis='y')
ege_pears_ax.get_legend().remove()

#Legend
handles, labels = ege_pears_ax.get_legend_handles_labels()
fig_pears.legend(handles, labels, loc=(0.45,0.02), ncol=4)
fig_pears.set_size_inches([11, 5])
fig_pears.tight_layout(rect=[0,0.1,1,1])

#%% Plot Spearman

# Re arrange dataframes
cge_spearman_df_m = cge_spearman_df.reset_index().rename(columns={"index":"method"})
cge_spearman_df_m = cge_spearman_df_m.melt(id_vars="method",var_name="threshold", value_name="spearman")
ege_spearman_df_m = ege_spearman_df.reset_index().rename(columns={"index":"method"})
ege_spearman_df_m = ege_spearman_df_m.melt(id_vars="method",var_name="threshold", value_name="spearman")

# Set seaborn style
sb.set_style("darkgrid")
sb.set_context(rc={"axes.titlesize":12,"axes.labelsize":11, 
                   "xtick.labelsize":10, "ytick.labelsize":10, "legend.fontsize":10})


# Subplots
fig_spear, (cge_spear_ax, ege_spear_ax) = plt.subplots(nrows=1, ncols=2, sharey=True)

# Enable minor ticks
plt.minorticks_on()

# CONVENTIONAL
#Plot
sb.stripplot(data=cge_spearman_df_m, y="method", x="spearman", hue="threshold", dodge=True, s=6,
             ax=cge_spear_ax)
cge_spear_ax.set(xlim=(0.75,1.02), xlabel="$\\rho$", ylabel="", title="CONVENTIONAL")
cge_spear_ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
cge_spear_ax.grid(which='minor', axis='y')
cge_spear_ax.get_legend().remove()

# ENHANCED
# Rearrange dataframe
#Plot
sb.stripplot(data=ege_spearman_df_m, y="method", x="spearman", hue="threshold", dodge=True, s=6,
             ax=ege_spear_ax)
ege_spear_ax.set(xlim=(0.75,1.02), xlabel="$\\rho$", ylabel="", title="ENHANCED")
ege_spear_ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
ege_spear_ax.grid(which='minor', axis='y')
ege_spear_ax.get_legend().remove()

#Legend
handles, labels = ege_spear_ax.get_legend_handles_labels()
fig_spear.legend(handles, labels, loc=(0.45,0.02), ncol=4)
fig_spear.set_size_inches([11, 5])
fig_spear.tight_layout(rect=[0,0.1,1,1])


#%% Save
fig_pears.savefig(os.path.join(folder_OUT, file_name + "_Pearson.tiff"), dpi=300)
fig_spear.savefig(os.path.join(folder_OUT, file_name + "_Spearman.tiff"), dpi=300)

#%% Calculate and plot enhanced ony, with outliers

qt = 1
ege_pearson_all, ege_spearman_all = {}, {}
for method in ILCD:
    df = ege_df[ege_df.method == method[2]]
    sp_={}
    pe_={}
    for t in threshold:
        qt_val = df.Reference.quantile(qt)
        mask = np.where(df.Reference<qt_val, True, False)
        sp_[t] = spearmanr(df["Reference"][mask], df["Simplified_"+str(t)][mask])[0]
        pe_[t] = pearsonr(df["Reference"][mask], df["Simplified_"+str(t)][mask])[0]
        ege_spearman_all[method[2]] = sp_
        ege_pearson_all[method[2]] = pe_

ege_pearson_all_df = pd.DataFrame.from_dict(ege_pearson_all, orient="index")
ege_pearson_all_df.columns = ["{:.0%}".format(t) for t in ege_pearson_all_df.columns]
ege_spearman_all_df = pd.DataFrame.from_dict(ege_spearman_all, orient="index")
ege_spearman_all_df.columns = ["{:.0%}".format(t) for t in ege_spearman_all_df.columns]


# Re arrange dataframes
ege_spearman_all_df_m = ege_spearman_all_df.reset_index().rename(columns={"index":"method"})
ege_spearman_all_df_m = ege_spearman_all_df_m.melt(id_vars="method",var_name="threshold", value_name="spearman")
ege_pearson_all_df_m = ege_pearson_all_df.reset_index().rename(columns={"index":"method"})
ege_pearson_all_df_m = ege_pearson_all_df_m.melt(id_vars="method",var_name="threshold", value_name="pearson")


sb.set_style("darkgrid")
sb.set_context(rc={"axes.titlesize":12,"axes.labelsize":11, 
                   "xtick.labelsize":10, "ytick.labelsize":10, "legend.fontsize":10})

fig_enh, (ege_pears_ax, ege_spear_ax) = plt.subplots(nrows=1, ncols=2, sharey=True)
plt.minorticks_on()

#Pearson
sb.stripplot(data=ege_pearson_all_df_m, y="method", x="pearson", hue="threshold", dodge=True, s=6,
             ax=ege_pears_ax)
ege_pears_ax.set(xlim=(0.7,1.02), xlabel="r", ylabel="")
ege_pears_ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
ege_pears_ax.grid(which='minor', axis='y')
ege_pears_ax.get_legend().remove()

#Spearman
sb.stripplot(data=ege_spearman_all_df_m, y="method", x="spearman", hue="threshold", dodge=True, s=6,
             ax=ege_spear_ax)
ege_spear_ax.set(xlim=(0.7,1.02), xlabel="$\\rho$", ylabel="")
ege_spear_ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
ege_spear_ax.grid(which='minor', axis='y')
ege_spear_ax.get_legend().remove()

#Legend
handles, labels = ege_spear_ax.get_legend_handles_labels()
fig_enh.suptitle("ENHANCED, WITH OUTLIERS")
fig_enh.legend(handles, labels, loc=(0.45,0.02), ncol=4)
fig_enh.set_size_inches([11, 5])
fig_enh.tight_layout(rect=[0,0.1,1,0.95])

fig_enh.savefig(os.path.join(folder_OUT, file_name + "_ENH_W-OUTL.tiff"), dpi=300)
