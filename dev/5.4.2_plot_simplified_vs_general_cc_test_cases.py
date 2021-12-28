#%% Set-up
import bw2data as bd
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
from matplotlib.ticker import FormatStrFormatter
from matplotlib.lines import Line2D
from pathlib import Path

# Import local
from gsa_geothermal.utils import get_EF_methods
from gsa_geothermal.data import (
    get_df_carbon_footprints_from_literature_conventional,
    get_df_carbon_footprints_from_literature_enhanced
)

# Set project
bd.projects.set_current("Geothermal")

# Method
method = get_EF_methods(select_climate_change_only=True)

# Load general model data
write_dir_validation = Path("write_files") / "validation"
iterations = 10000
seed = 13413203
filename_conventional_general = "{}.{}.all_categories.N{}.seed{}.json".format(
    "conventional", "general", iterations, seed,
)
filename_enhanced_general = "{}.{}.all_categories.N{}.seed{}.json".format(
    "enhanced", "general", iterations, seed
)
filepath_conventional_general = write_dir_validation / filename_conventional_general
filepath_enhanced_general = write_dir_validation / filename_enhanced_general
df_general_model_conv = (
    pd.read_json(filepath_conventional_general)[
        "climate change no LT"
    ]
    * 1000
)
df_general_model_enh = (
        pd.read_json(filepath_enhanced_general)[
            "climate change no LT"
        ]
        * 1000
)

# Load and rearrange literature data
df_conventional_literature = get_df_carbon_footprints_from_literature_conventional()
df_enhanced_literature = get_df_carbon_footprints_from_literature_enhanced()

df_conventional_literature = df_conventional_literature.dropna(subset=["Operational CO2 emissions (g/kWh)"]).reset_index(
    drop=True
)
# df_conventional_literature = df_conventional_literature.iloc[[4,5,6,7]]
df_conventional_literature = df_conventional_literature[df_conventional_literature.columns[[0, 2]]]
df_conventional_literature.columns = ["study", "carbon footprint"]
df_conventional_literature = df_conventional_literature.sort_values(by="study")

df_enhanced_literature = df_enhanced_literature[df_enhanced_literature.columns[[0, 2]]]
df_enhanced_literature.columns = ["study", "carbon footprint"]
df_enhanced_literature = df_enhanced_literature.sort_values(by="study")

# Load simplified model scores
filename_conventional_simplified = "{}.{}.cc_test_cases.ch4_{}.json".format("conventional", "simplified", "True")
filename_conventional_simplified_ch4_false = "{}.{}.cc_test_cases.ch4_{}.json".format("conventional", "simplified", "False")
filename_enhanced_simplified = "{}.{}.cc_test_cases.json".format("enhanced", "simplified")

filepath_conventional_simplified = write_dir_validation / filename_conventional_simplified
filepath_conventional_simplified_ch4_false = write_dir_validation / filename_conventional_simplified_ch4_false
filepath_enhanced_simplified = write_dir_validation/ filename_enhanced_simplified

cge_s_df = pd.read_json(filepath_conventional_simplified)
cge_s_df_ch4_false = pd.read_json(filepath_conventional_simplified_ch4_false)
ege_s_df = pd.read_json(filepath_enhanced_simplified)

# save data
write_dir = Path("write_files") / "validation" / "figures"

#%% Plot - with CH4=True

sb.set_style("dark")
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
fig, (cge_ax, ege_ax) = plt.subplots(
    ncols=2, sharex="col", gridspec_kw={"width_ratios": [2, 3]}
)

# Distance between points
dist = 0.3

# Conventional

# Re-arrange dataframe
cge_s_df_2 = cge_s_df.rename(columns={"10%": "all thresholds"})
cge_s_df_2 = cge_s_df_2.melt(
    id_vars="study", var_name="simplified model", value_name="carbon footprint"
)
cge_lit = df_conventional_literature
cge_lit["type"] = "literature"

# Set positions
pos_cge_lit = np.arange(len(df_conventional_literature))
pos_cge_s = pos_cge_lit + dist
pos_cge_ticks = pos_cge_lit + dist / 2
pos_cge_ref = pos_cge_lit[-1] + 2
pos_cge_ticks = np.append(pos_cge_ticks, pos_cge_ref)
cge_ticklabels = cge_lit["study"].to_list()
cge_ticklabels.append("general model")

# Plot
cge_ax.boxplot(
    x=df_general_model_conv,
    positions=[pos_cge_ref],
    vert=True,
    whis=[1, 99],
    showfliers=False,
    widths=1,
    medianprops={"color": "black"},
)
sb.scatterplot(
    data=df_conventional_literature,
    y="carbon footprint",
    x=pos_cge_lit,
    style="type",
    markers=["s"],
    color="black",
    ax=cge_ax,
)
sb.scatterplot(
    data=cge_s_df_2,
    y="carbon footprint",
    x=pos_cge_s,
    hue="simplified model",
    ax=cge_ax,
)
cge_ax.set(
    ylabel="",
    xlabel="",
    xticks=pos_cge_ticks,
    xticklabels=cge_ticklabels,  # yscale="log",
    xlim=(pos_cge_ticks[0] - 0.5, pos_cge_ticks[-1] + 1),
)
cge_ax.grid(b=True, which="both", axis="y")
cge_ax.yaxis.set_minor_formatter(FormatStrFormatter("%.0f"))
cge_ax.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))
cge_ax.yaxis.set_major_locator(ticker.MultipleLocator(50))
cge_ax.tick_params(axis="x", which="both", labelrotation=90)
cge_ax.get_legend().remove()

# y-axis limits
cge_ax.set(ylim=(0, 1005))
cge_ax.set(ylabel="$\mathregular{g CO_2 eq./kWh}$")

# Title
cge_ax.set_title("CONVENTIONAL")

# Legend
handle_placeholder = Line2D([0],[0],color="w")
handles, labels = cge_ax.get_legend_handles_labels()
handles = [handles[0], handle_placeholder, handles[1]]
labels = [labels[0], "simplified model:", labels[1]]
cge_ax.legend(handles=handles, labels=labels, loc="upper right")

# Enhanced
# Re-arrange dataframe
ege_s_df_2 = ege_s_df.rename(columns={"10%": "10,15,20%"})
ege_s_df_2 = ege_s_df_2.melt(
    id_vars="study", var_name="simplified model", value_name="carbon footprint"
)
ege_lit = df_enhanced_literature
ege_lit["type"] = "literature"

# Set positions
pos_ege_lit = np.arange(len(df_enhanced_literature))
pos_ege_s = np.hstack([pos_ege_lit + dist, pos_ege_lit + dist])
pos_ege_ticks = pos_ege_lit + dist / 2
pos_ege_ref = pos_ege_lit[-1] + 2
pos_ege_ticks = np.append(pos_ege_ticks, pos_ege_ref)
ege_ticklabels = ege_lit["study"].to_list()
ege_ticklabels.append("general model")

# Plot
ege_ax.boxplot(
    x=df_general_model_enh,
    positions=[pos_ege_ref],
    vert=True,
    whis=[1, 99],
    showfliers=False,
    widths=1,
    medianprops={"color": "black"},
)
sb.scatterplot(
    data=df_enhanced_literature,
    y="carbon footprint",
    x=pos_ege_lit,
    style="type",
    markers=["s"],
    color="black",
    ax=ege_ax,
)
sb.scatterplot(
    data=ege_s_df_2,
    y="carbon footprint",
    x=pos_ege_s,
    hue="simplified model",
    ax=ege_ax,
)

ege_ax.set(
    ylabel="",
    xlabel="",
    xticks=pos_ege_ticks,
    xticklabels=ege_ticklabels,  # yscale="log",
    xlim=(pos_ege_ticks[0] - 0.5, pos_ege_ticks[-1] + 1),
)
ege_ax.grid(b=True, which="both", axis="y")
ege_ax.yaxis.set_minor_formatter(FormatStrFormatter("%.0f"))
ege_ax.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))
ege_ax.yaxis.set_major_locator(ticker.MultipleLocator(50))
ege_ax.tick_params(axis="x", labelrotation=90)
ege_ax.get_legend().remove()

# Limits
ege_ax.set(ylim=(0, 820))
ege_ax.set(ylabel="$\mathregular{g CO_2 eq./kWh}$")

# Title
ege_ax.set_title("ENHANCED")

handles, labels = ege_ax.get_legend_handles_labels()
handles = [handles[0], handle_placeholder, handles[1], handles[2]]
labels = [labels[0], "simplified model:", labels[1], labels[2]]
ege_ax.legend(handles=handles, labels=labels, loc="upper right")

fig.subplots_adjust(hspace=0.010)
fig.set_size_inches([11, 8])
fig.tight_layout()

# save plot
filename_plot = (
    "simplified_vs_general.cc_test_cases.N{}.seed{}.tiff".format(iterations, seed)
)
filepath_plot = write_dir / filename_plot
print("Saving {}".format(filepath_plot))
fig.savefig((filepath_plot), dpi=300)


#%% Plot - conventional ONLY with CH4 = False

# Subplots
fig, cge_ax_ch4_false = plt.subplots(nrows=1, ncols=1, sharex="col")

# Distance between points
dist = 0.3

# Re-arrange dataframe
cge_s_df_ch4_false_2 = cge_s_df_ch4_false.rename(columns={"10%": "all thresholds"})
cge_s_df_ch4_false_2 = cge_s_df_ch4_false_2.melt(
    id_vars="study", var_name="simplified model", value_name="carbon footprint"
)
cge_lit = df_conventional_literature
cge_lit["type"] = "literature"

# Plot
cge_ax_ch4_false.boxplot(
    x=df_general_model_conv,
    positions=[pos_cge_ref],
    vert=True,
    whis=[1, 99],
    showfliers=False,
    widths=1,
    medianprops={"color": "black"},
)
sb.scatterplot(
    data=df_conventional_literature,
    y="carbon footprint",
    x=pos_cge_lit,
    style="type",
    markers=["s"],
    color="black",
    ax=cge_ax_ch4_false,
)
sb.scatterplot(
    data=cge_s_df_ch4_false_2,
    y="carbon footprint",
    x=pos_cge_s,
    hue="simplified model",
    ax=cge_ax_ch4_false,
)
cge_ax_ch4_false.set(
    ylabel="",
    xlabel="",
    xticks=pos_cge_ticks,
    xticklabels=cge_ticklabels,  # yscale="log",
    xlim=(pos_cge_ticks[0] - 0.5, pos_cge_ticks[-1] + 1),
)
cge_ax_ch4_false.grid(b=True, which="both", axis="y")
cge_ax_ch4_false.yaxis.set_minor_formatter(FormatStrFormatter("%.0f"))
cge_ax_ch4_false.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))
cge_ax_ch4_false.yaxis.set_major_locator(ticker.MultipleLocator(50))
cge_ax_ch4_false.tick_params(axis="x", which="both", labelrotation=90)
cge_ax_ch4_false.get_legend().remove()

# y-axis limits
cge_ax_ch4_false.set(ylim=(0, 830))
cge_ax_ch4_false.set_ylabel("$\mathregular{g CO_2 eq./kWh}$")

# Title
cge_ax_ch4_false.set_title("CONVENTIONAL")

# Legend
handles, labels = cge_ax_ch4_false.get_legend_handles_labels()
handles = [handles[0], handle_placeholder, handles[1]]
labels = [labels[0], "simplified model:", labels[1]]
cge_ax_ch4_false.legend(handles=handles, labels=labels, loc="upper right")

fig.subplots_adjust(hspace=0.010)
fig.set_size_inches([4.4, 8])
fig.tight_layout()

# save plot
filename_plot_ch4_false = (
    "simplified_vs_general.cc_test_cases.conventiona_ch4_false.N{}.seed{}.tiff".format(iterations, seed)
)
filepath_plot_ch4_false = write_dir / filename_plot_ch4_false
print("Saving {}".format(filepath_plot))
fig.savefig((filepath_plot_ch4_false), dpi=300)
