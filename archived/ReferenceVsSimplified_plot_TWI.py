#%% Set up and load data
import brightway2 as bw
import seaborn as sb
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from scipy.stats import spearmanr, pearsonr

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
n_iter = 10000
threshold_cge = 0.15
threshold_ege = 0.15

ecoinvent_version = "ecoinvent_3.6"
folder_IN = os.path.join(
    absolute_path, "generated_files", ecoinvent_version, "validation"
)
file_name = "ReferenceVsSimplified_N" + str(n_iter)

cge_ref_df = pd.read_json(
    os.path.join(folder_IN, file_name + "_Conventional_Reference")
).melt(var_name="method", value_name="Reference")
cge_s_df = pd.read_json(
    os.path.join(
        folder_IN, file_name + "_Conventional_Simplified_t" + str(threshold_cge)
    )
).melt(var_name="method", value_name="Simplified")
cge_df = pd.concat([cge_ref_df, cge_s_df["Simplified"]], axis=1)

ege_ref_df = pd.read_json(
    os.path.join(folder_IN, file_name + "_Enhanced_Reference")
).melt(var_name="method", value_name="Reference")
ege_s_df = pd.read_json(
    os.path.join(folder_IN, file_name + "_Enhanced_Simplified_t" + str(threshold_ege))
).melt(var_name="method", value_name="Simplified")
ege_df = pd.concat([ege_ref_df, ege_s_df["Simplified"]], axis=1)

folder_OUT = os.path.join(absolute_path, "generated_plots", ecoinvent_version)

#%% Calculate pearson

cge_pearson, cge_spearman = {}, {}
for method in ILCD:
    df = cge_df[cge_df.method == method[2]]
    sp_ = spearmanr(df["Reference"], df["Simplified"])[0]
    pe_ = pearsonr(df["Reference"], df["Simplified"])[0]
    cge_spearman[method[2]] = sp_
    cge_pearson[method[2]] = pe_

cge_pearson_df = pd.DataFrame.from_dict(cge_pearson, orient="index")
cge_pearson_df.columns = ["Pearson"]
cge_spearman_df = pd.DataFrame.from_dict(cge_spearman, orient="index")
cge_spearman_df.columns = ["Spearman"]

# Remove outliers
ege_pearson, ege_spearman = {}, {}
for method in ILCD:
    df = ege_df[ege_df.method == method[2]]
    sp_ = spearmanr(df["Reference"], df["Simplified"])[0]
    pe_ = pearsonr(df["Reference"], df["Simplified"])[0]
    ege_spearman[method[2]] = sp_
    ege_pearson[method[2]] = pe_

ege_pearson_df = pd.DataFrame.from_dict(ege_pearson, orient="index")
ege_pearson_df.columns = ["Pearson"]
ege_spearman_df = pd.DataFrame.from_dict(ege_spearman, orient="index")
ege_spearman_df.columns = ["Spearman"]

#%% Parity plot coloured according to density

from scipy.stats import gaussian_kde as kde
from matplotlib.colors import Normalize
from matplotlib import cm
from utils.plot_funcs import set_axlims


cge_parityplot_col = plt.figure()
for i, method in enumerate(ILCD):
    ax_ = cge_parityplot_col.add_subplot(4, 4, i + 1)
    df = cge_df[cge_df.method == method[2]]

    # Calculate kde density values
    df_ = df[["Reference", "Simplified"]].to_numpy().T
    kde_v = kde(df[["Reference", "Simplified"]].to_numpy().T).evaluate(df_)

    # Sort kde value and df values by kde values
    kde_sort = kde_v.argsort()
    df_sort = df.iloc[kde_sort]
    kde_v_sort = kde_v[kde_sort]

    # Find axis limits
    x_lim = set_axlims(df.Reference, 0.02)
    y_lim = set_axlims(df.Simplified, 0.02)
    lim = (0, max(x_lim[1], y_lim[1]))

    # Parity plot
    sb.lineplot(x=[0, 1e10], y=[0, 1e10], color="black", ax=ax_, linewidth=1)
    plt.scatter(
        x=df_sort.Reference,
        y=df_sort.Simplified,
        s=7,
        c=kde_v_sort,
        cmap="cool",
        linewidth=0,
    )

    # Add colorbar
    cbar = plt.colorbar()
    cbar.formatter.set_powerlimits((0, 0))
    cbar.ax.yaxis.set_offset_position("left")
    cbar.set_label("KDE", rotation=270, labelpad=10)

    # Add text
    tx = "r: " + str(round(cge_pearson[method[2]], 2))
    ax_.text(0.05, 0.9, tx, transform=ax_.transAxes, fontsize=8)
    tx_2 = "$\\rho$: " + str(round(cge_spearman[method[2]], 2))
    ax_.text(0.05, 0.8, tx_2, transform=ax_.transAxes, fontsize=8)

    # Amend other features
    plt.xlim(lim)
    plt.ylim(lim)
    ax_.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))
    title_ = ILCD[i][2] + "\n" + "[" + ILCD_units[i] + "]"
    ax_.set_title(label=title_, fontsize=9)
    ax_.set(xlabel="", ylabel="")
cge_parityplot_col.text(
    0.5, 0.01, "Full model", ha="center", fontsize=12, fontweight="bold"
)
cge_parityplot_col.text(
    0.01,
    0.5,
    "Simplified model",
    va="center",
    rotation="vertical",
    fontsize=12,
    fontweight="bold",
)


ege_parityplot_col = plt.figure()
for i, method in enumerate(ILCD):
    ax_ = ege_parityplot_col.add_subplot(4, 4, i + 1)
    df = ege_df[ege_df.method == method[2]]

    # Calculate kde density values
    df_ = df[["Reference", "Simplified"]].to_numpy().T
    kde_v = kde(df[["Reference", "Simplified"]].to_numpy().T).evaluate(df_)

    # Sort kde value and df values by kde values
    kde_sort = kde_v.argsort()
    df_sort = df.iloc[kde_sort]
    kde_v_sort = kde_v[kde_sort]

    # Find axis limits
    x_lim = set_axlims(df.Reference, 0.02)
    y_lim = set_axlims(df.Simplified, 0.02)
    lim = (0, max(x_lim[1], y_lim[1]))

    # Parity plot
    sb.lineplot(x=[0, 1e10], y=[0, 1e10], color="black", ax=ax_, linewidth=1)
    plt.scatter(
        x=df_sort.Reference,
        y=df_sort.Simplified,
        s=7,
        c=kde_v_sort,
        cmap="cool",
        linewidth=0,
    )
    plt.locator_params(axis="both", nbins=4)

    # Add color bar
    cbar = plt.colorbar()
    cbar.formatter.set_powerlimits((0, 0))
    cbar.ax.yaxis.set_offset_position("left")
    cbar.set_label("KDE", rotation=270, labelpad=10)

    # Add text
    tx = "r: " + str(round(ege_pearson[method[2]], 2))
    ax_.text(0.05, 0.9, tx, transform=ax_.transAxes, fontsize=8)
    tx_2 = "$\\rho$: " + str(round(ege_spearman[method[2]], 2))
    ax_.text(0.05, 0.8, tx_2, transform=ax_.transAxes, fontsize=8)

    # Amend other features
    plt.xlim(lim)
    plt.ylim(lim)
    ax_.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))
    title_ = ILCD[i][2] + "\n" + "[" + ILCD_units[i] + "]"
    ax_.set_title(label=title_, fontsize=9)
    ax_.set(xlabel="", ylabel="")
ege_parityplot_col.text(
    0.5, 0.01, "Full model", ha="center", fontsize=12, fontweight="bold"
)
ege_parityplot_col.text(
    0.01,
    0.5,
    "Simplified model",
    va="center",
    rotation="vertical",
    fontsize=12,
    fontweight="bold",
)

cge_parityplot_col.suptitle("CONVENTIONAL")
ege_parityplot_col.suptitle("ENHANCED")

cge_parityplot_col.set_size_inches([13, 14.5])
ege_parityplot_col.set_size_inches([13, 14.5])
cge_parityplot_col.tight_layout(rect=[0.02, 0.02, 1, 0.95])
ege_parityplot_col.tight_layout(rect=[0.02, 0.02, 1, 0.95])

cge_parityplot_col.subplots_adjust(hspace=0.5)
ege_parityplot_col.subplots_adjust(hspace=0.5)

#%% Save figures
file_name_par_col = file_name + " Parity_Plot_COL_TWI"
cge_parityplot_col.savefig(
    os.path.join(
        folder_OUT, file_name_par_col + "_Conventional_t" + str(threshold_cge) + ".tiff"
    ),
    dpi=300,
)
ege_parityplot_col.savefig(
    os.path.join(
        folder_OUT, file_name_par_col + "_Enhanced_t" + str(threshold_cge) + ".tiff"
    ),
    dpi=300,
)
