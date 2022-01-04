#%% Set up and load data
import brightway2 as bw
import seaborn as sb
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr
from matplotlib import ticker
from pathlib import Path

# Import local
from gsa_geothermal.utils import get_EF_methods

if __name__ == '__main__':
    # Set project
    bw.projects.set_current("Geothermal")
    
    # Methods
    methods, methods_units = get_EF_methods(return_units=True)
    
    # Options
    iterations = 10000
    seed = 13413203
    thresholds = [0.2, 0.15, 0.1, 0.05]
    
    # Load data
    write_dir_validation = Path("write_files") / "validation"
    
    filename_conventional_general = "{}.{}.all_categories.N{}.seed{}.json".format("conventional", "general", iterations, seed)
    filename_enhanced_general = "{}.{}.all_categories.N{}.seed{}.json".format("enhanced", "general", iterations,seed)
    filepath_conventional_general = write_dir_validation / filename_conventional_general
    filepath_enhanced_general = write_dir_validation / filename_enhanced_general
    cge_gen_df = pd.read_json(filepath_conventional_general).melt(var_name="method", value_name="general")
    ege_gen_df = pd.read_json(filepath_enhanced_general).melt(var_name="method", value_name="general")

    cge_s_df = {}
    ege_s_df = {}
    for t in thresholds:
        filename_conventional_simplified = "{}.{}.t{:02d}.all_categories.N{}.seed{}.json".format("conventional", "simplified", int(t*100), iterations, seed)
        filename_enhanced_simplified = "{}.{}.t{:02d}.all_categories.N{}.seed{}.json".format("enhanced", "simplified", int(t*100), iterations, seed)
        filepath_conventional_simplified = write_dir_validation / filename_conventional_simplified
        filepath_enhanced_simplified = write_dir_validation/ filename_enhanced_simplified
        cge_s_df[t] = pd.read_json(filepath_conventional_simplified).melt(var_name="method", value_name="simplified_" + str(t))
        ege_s_df[t] = pd.read_json(filepath_enhanced_simplified).melt(var_name="method", value_name="simplified_" + str(t))
    
    cge_df = cge_gen_df
    ege_df = ege_gen_df
    for t in thresholds:
        cge_df = pd.concat([cge_df, cge_s_df[t]["simplified_" + str(t)]], axis=1)
        ege_df = pd.concat([ege_df, ege_s_df[t]["simplified_" + str(t)]], axis=1)           
        
    # save data
    write_dir_figures = write_dir_validation / "figures"
    write_dir_figures.mkdir(parents=True, exist_ok=True)
    
    # Fix methods names for plots
    methods_plots = []
    for m_ in methods:
        methods_plots.append(m_[1][:-6])

#%% CALCULATE PEARSON AND SPEARMAN CORRELATION COEFFICIENTS

cge_pearson, cge_spearman = {}, {}
for method in methods:
    df = cge_df[cge_df.method == method[1]]
    sp_ = {}
    pe_ = {}
    for t in thresholds:
        sp_[t] = spearmanr(df["general"], df["simplified_" + str(t)])[0]
        pe_[t] = pearsonr(df["general"], df["simplified_" + str(t)])[0]
        cge_spearman[method[1]] = sp_
        cge_pearson[method[1]] = pe_

cge_pearson_df = pd.DataFrame.from_dict(cge_pearson, orient="index")
cge_pearson_df.columns = ["{:.0%}".format(t) for t in cge_pearson_df.columns]
cge_spearman_df = pd.DataFrame.from_dict(cge_spearman, orient="index")
cge_spearman_df.columns = ["{:.0%}".format(t) for t in cge_spearman_df.columns]

# Remove outliers
qt = 0.999
ege_pearson, ege_spearman = {}, {}
for method in methods:
    df = ege_df[ege_df.method == method[1]]
    sp_ = {}
    pe_ = {}
    for t in thresholds:
        qt_val = df.general.quantile(qt)
        mask = np.where(df.general < qt_val, True, False)
        sp_[t] = spearmanr(df["general"][mask], df["simplified_" + str(t)][mask])[0]
        pe_[t] = pearsonr(df["general"][mask], df["simplified_" + str(t)][mask])[0]
        ege_spearman[method[1]] = sp_
        ege_pearson[method[1]] = pe_

ege_pearson_df = pd.DataFrame.from_dict(ege_pearson, orient="index")
ege_pearson_df.columns = ["{:.0%}".format(t) for t in ege_pearson_df.columns]
ege_spearman_df = pd.DataFrame.from_dict(ege_spearman, orient="index")
ege_spearman_df.columns = ["{:.0%}".format(t) for t in ege_spearman_df.columns]

#%% PLOT PEARSON

# Re arrange dataframes
cge_pearson_df_m = cge_pearson_df.reset_index().rename(columns={"index": "method"})
cge_pearson_df_m = cge_pearson_df_m.melt(
    id_vars="method", var_name="threshold", value_name="pearson"
)
cge_pearson_df_m["method"] = cge_pearson_df_m["method"].str.replace(' no LT', '')

ege_pearson_df_m = ege_pearson_df.reset_index().rename(columns={"index": "method"})
ege_pearson_df_m = ege_pearson_df_m.melt(
    id_vars="method", var_name="threshold", value_name="pearson"
)
ege_pearson_df_m["method"] = ege_pearson_df_m["method"].str.replace(' no LT', '')

# Set seaborn style
sb.set_style("darkgrid")
sb.set_context(
    rc={
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
    }
)

# Subplots
fig_pears, (cge_pears_ax, ege_pears_ax) = plt.subplots(nrows=1, ncols=2, sharey=True)

# Enable minor ticks
plt.minorticks_on()

# Set xticks
xticks = [0.8, 0.85, 0.9, 0.95, 1]

# CONVENTIONAL
# Plot
sb.stripplot(
    data=cge_pearson_df_m,
    y="method",
    x="pearson",
    hue="threshold",
    dodge=True,
    s=6,
    ax=cge_pears_ax,
)
cge_pears_ax.set(
    xlim=(0.8, 1.01), xlabel="r", ylabel="", title="CONVENTIONAL", xticks=xticks
)
cge_pears_ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
cge_pears_ax.grid(which="minor", axis="y")
cge_pears_ax.get_legend().remove()

# ENHANCED
# Plot
sb.stripplot(
    data=ege_pearson_df_m,
    y="method",
    x="pearson",
    hue="threshold",
    dodge=True,
    s=6,
    ax=ege_pears_ax,
)
ege_pears_ax.set(
    xlim=(0.8, 1.01), xlabel="r", ylabel="", title="ENHANCED", xticks=xticks
)
ege_pears_ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
ege_pears_ax.grid(which="minor", axis="y")
ege_pears_ax.get_legend().remove()

# Legend
handles, labels = ege_pears_ax.get_legend_handles_labels()
fig_pears.legend(handles, labels, loc=(0.45, 0.02), ncol=4)
fig_pears.set_size_inches([11, 5])
fig_pears.tight_layout(rect=[0, 0.1, 1, 1])

# save plot
filename_pears_plot = "pearson_plot.simplified_vs_general.N{}.seed{}.tiff".format(iterations, seed)
filepath_pears_plot = write_dir_figures /  filename_pears_plot
print("Saving {}".format(filepath_pears_plot))
fig_pears.savefig(filepath_pears_plot, dpi=300)

#%% PLOT SPEARMAN

# Re arrange dataframes
cge_spearman_df_m = cge_spearman_df.reset_index().rename(columns={"index": "method"})
cge_spearman_df_m = cge_spearman_df_m.melt(
    id_vars="method", var_name="threshold", value_name="spearman"
)
cge_spearman_df_m["method"] = cge_spearman_df_m["method"].str.replace(' no LT', '')

ege_spearman_df_m = ege_spearman_df.reset_index().rename(columns={"index": "method"})
ege_spearman_df_m = ege_spearman_df_m.melt(
    id_vars="method", var_name="threshold", value_name="spearman"
)
ege_spearman_df_m["method"] = ege_spearman_df_m["method"].str.replace(' no LT', '')

# Set seaborn style
sb.set_style("darkgrid")
sb.set_context(
    rc={
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
    }
)


# Subplots
fig_spear, (cge_spear_ax, ege_spear_ax) = plt.subplots(nrows=1, ncols=2, sharey=True)

# Enable minor ticks
plt.minorticks_on()

# CONVENTIONAL
# Plot
sb.stripplot(
    data=cge_spearman_df_m,
    y="method",
    x="spearman",
    hue="threshold",
    dodge=True,
    s=6,
    ax=cge_spear_ax,
)
cge_spear_ax.set(xlim=(0.75, 1.02), xlabel="$\\rho$", ylabel="", title="CONVENTIONAL")
cge_spear_ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
cge_spear_ax.grid(which="minor", axis="y")
cge_spear_ax.get_legend().remove()

# ENHANCED
# Rearrange dataframe
# Plot
sb.stripplot(
    data=ege_spearman_df_m,
    y="method",
    x="spearman",
    hue="threshold",
    dodge=True,
    s=6,
    ax=ege_spear_ax,
)
ege_spear_ax.set(xlim=(0.75, 1.02), xlabel="$\\rho$", ylabel="", title="ENHANCED")
ege_spear_ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
ege_spear_ax.grid(which="minor", axis="y")
ege_spear_ax.get_legend().remove()

# Legend
handles, labels = ege_spear_ax.get_legend_handles_labels()
fig_spear.legend(handles, labels, loc=(0.45, 0.02), ncol=4)
fig_spear.set_size_inches([11, 5])
fig_spear.tight_layout(rect=[0, 0.1, 1, 1])

# Save plot
filename_spear_plot = "spearman_plot.simplified_vs_general.N{}.seed{}.tiff".format(iterations, seed)
filepath_spear_plot = write_dir_figures /  filename_spear_plot
print("Saving {}".format(filepath_spear_plot))
fig_pears.savefig(filepath_spear_plot, dpi=300)


#%% CALCULATE AND PLOT, PEARSON AND SPEARMAN - ENHANCED ONLY

qt = 1
ege_pearson_all, ege_spearman_all = {}, {}
for method in methods:
    df = ege_df[ege_df.method == method[1]]
    sp_ = {}
    pe_ = {}
    for t in thresholds:
        qt_val = df.general.quantile(qt)
        mask = np.where(df.general < qt_val, True, False)
        sp_[t] = spearmanr(df["general"][mask], df["simplified_" + str(t)][mask])[0]
        pe_[t] = pearsonr(df["general"][mask], df["simplified_" + str(t)][mask])[0]
        ege_spearman_all[method[1]] = sp_
        ege_pearson_all[method[1]] = pe_

ege_pearson_all_df = pd.DataFrame.from_dict(ege_pearson_all, orient="index")
ege_pearson_all_df.columns = ["{:.0%}".format(t) for t in ege_pearson_all_df.columns]
ege_spearman_all_df = pd.DataFrame.from_dict(ege_spearman_all, orient="index")
ege_spearman_all_df.columns = ["{:.0%}".format(t) for t in ege_spearman_all_df.columns]


# Re arrange dataframes
ege_spearman_all_df_m = ege_spearman_all_df.reset_index().rename(
    columns={"index": "method"}
)
ege_spearman_all_df_m = ege_spearman_all_df_m.melt(
    id_vars="method", var_name="threshold", value_name="spearman"
)
ege_pearson_all_df_m = ege_pearson_all_df.reset_index().rename(
    columns={"index": "method"}
)
ege_pearson_all_df_m = ege_pearson_all_df_m.melt(
    id_vars="method", var_name="threshold", value_name="pearson"
)
ege_pearson_all_df_m["method"] = ege_pearson_df_m["method"].str.replace(' no LT', '')
ege_spearman_all_df_m["method"] = ege_spearman_df_m["method"].str.replace(' no LT', '')


sb.set_style("darkgrid")
sb.set_context(
    rc={
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
    }
)

fig_enh, (ege_pears_ax, ege_spear_ax) = plt.subplots(nrows=1, ncols=2, sharey=True)
plt.minorticks_on()

# Pearson
sb.stripplot(
    data=ege_pearson_all_df_m,
    y="method",
    x="pearson",
    hue="threshold",
    dodge=True,
    s=6,
    ax=ege_pears_ax,
)
ege_pears_ax.set(xlim=(0.7, 1.02), xlabel="r", ylabel="")
ege_pears_ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
ege_pears_ax.grid(which="minor", axis="y")
ege_pears_ax.get_legend().remove()

# Spearman
sb.stripplot(
    data=ege_spearman_all_df_m,
    y="method",
    x="spearman",
    hue="threshold",
    dodge=True,
    s=6,
    ax=ege_spear_ax,
)
ege_spear_ax.set(xlim=(0.7, 1.02), xlabel="$\\rho$", ylabel="")
ege_spear_ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
ege_spear_ax.grid(which="minor", axis="y")
ege_spear_ax.get_legend().remove()

# Legend
handles, labels = ege_spear_ax.get_legend_handles_labels()
fig_enh.suptitle("ENHANCED, WITH OUTLIERS")
fig_enh.legend(handles, labels, loc=(0.45, 0.02), ncol=4)
fig_enh.set_size_inches([11, 5])
fig_enh.tight_layout(rect=[0, 0.1, 1, 0.95])

# Save plot
filename_enh_plot = "enhanced_pearson_spearman_plot.simplified_vs_general.N{}.seed{}.tiff".format(iterations, seed)
filepath_enh_plot = write_dir_figures /  filename_enh_plot
print("Saving {}".format(filepath_enh_plot))
fig_enh.savefig(filepath_enh_plot, dpi=300)
