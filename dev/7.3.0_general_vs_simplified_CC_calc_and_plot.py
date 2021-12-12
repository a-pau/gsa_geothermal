#%% Set-up
import brightway2 as bw
import pandas as pd
import os
import warnings
import seaborn as sb
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
from matplotlib.ticker import FormatStrFormatter

# Import local
from setup_files_gsa import setup_gt_project, get_ILCD_methods, run_mc
from simplified_gt_models import ConventionalSimplifiedModel as cge_model_s_
from simplified_gt_models import EnhancedSimplifiedModel as ege_model_s_

# Set working directory
path = "."
os.chdir(path)

# Set project
bw.projects.set_current("Geothermal")

# Retrieve methods
ILCD_CC = get_ILCD_methods(CC_only=True)

# Folder and file name for saving
ecoinvent_version = "ecoinvent_3.6"
absolute_path = os.path.abspath(path)
folder_OUT = os.path.join(absolute_path, "generated_plots", ecoinvent_version)
file_name = "ReferenceVsSimplified_test_cases_CC"

# Load parameters and carbon footprints
cge_data = pd.read_excel(
    os.path.join(
        absolute_path, "data_and_models/Carbon footprints from literature.xlsx"
    ),
    sheet_name="Conventional",
    index_col=None,
    skiprows=1,
)
ege_data = pd.read_excel(
    os.path.join(
        absolute_path, "data_and_models/Carbon footprints from literature.xlsx"
    ),
    sheet_name="Enhanced",
    index_col=None,
    skiprows=1,
    nrows=13,
)

# Re-arrange
cge_data = cge_data.dropna(subset=["Operational CO2 emissions (g/kWh)"]).reset_index(
    drop=True
)
# cge_data = cge_data.iloc[[4,5,6,7]]
cge_data = cge_data[cge_data.columns[[0, 2, 3]]]
cge_data.columns = ["study", "carbon footprint", "co2_emissions"]
cge_data["co2_emissions"] = cge_data["co2_emissions"] / 1000
cge_data = cge_data.sort_values(by="study")

ege_data = ege_data[ege_data.columns[[0, 2, 3, 4, 5, 6]]]
ege_data.columns = [
    "study",
    "carbon footprint",
    "specific_diesel_consumption",
    "installed_capacity",
    "average_depth_of_wells",
    "success_rate_primary_wells",
]
ege_data["specific_diesel_consumption"] = ege_data["specific_diesel_consumption"] * 1000
ege_data = ege_data.sort_values(by="study")

# Load reference model
n_iter = 10000
folder_IN = os.path.join(
    absolute_path, "generated_files", ecoinvent_version, "validation"
)
file_name_IN = "ReferenceVsSimplified_N" + str(n_iter)
cge_ref_df = (
    pd.read_json(os.path.join(folder_IN, file_name_IN + "_Conventional_Reference"))[
        "climate change total"
    ]
    * 1000
)
ege_ref_df = (
    pd.read_json(os.path.join(folder_IN, file_name_IN + "_Enhanced_Reference"))[
        "climate change total"
    ]
    * 1000
)

#%% Initialize classes
# Set threshold
# Note that only these thresholds are needed for CC
threshold_cge = [0.1]
threshold_ege = [0.1, 0.05]

# Conventional
cge_model_s = {}
for t in threshold_cge:
    cge_model_s[t] = cge_model_s_(t)

# Enhanced
ege_model_s = {}
for t in threshold_ege:
    ege_model_s[t] = ege_model_s_(t)

#%% Compute simplified

# Conventional
cge_s = {}
for t in threshold_cge:
    temp_ = {}
    for _, rows in cge_data.iterrows():
        # Values are multplied by 1000 to get gCO2 eq
        temp_[rows["study"]] = (
            cge_model_s[t].run(rows, lcia_methods=ILCD_CC)[ILCD_CC[0][-1]] * 1000
        )
    cge_s[t] = temp_

# Re-arrange results
cge_s_df = pd.DataFrame.from_dict(cge_s)
cge_s_df.columns = ["{:.0%}".format(t) for t in cge_s_df.columns]
cge_s_df = cge_s_df.reset_index().rename(columns={"index": "study"})

# Enhanced
ege_s = {}
for t in threshold_ege:
    temp_ = {}
    for _, rows in ege_data.iterrows():
        # Values are multplied by 1000 to get gCO2 eq
        temp_[rows["study"]] = (
            ege_model_s[t].run(rows, lcia_methods=ILCD_CC)[ILCD_CC[0][-1]] * 1000
        )
    ege_s[t] = temp_

# Re-arrange results
ege_s_df = pd.DataFrame.from_dict(ege_s)
ege_s_df.columns = ["{:.0%}".format(t) for t in ege_s_df.columns]
ege_s_df = ege_s_df.reset_index().rename(columns={"index": "study"})


#%% Plot

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
cge_lit = cge_data
cge_lit["type"] = "literature"

# Set positions
pos_cge_lit = np.arange(len(cge_data))
pos_cge_s = pos_cge_lit + dist
pos_cge_ticks = pos_cge_lit + dist / 2
pos_cge_ref = pos_cge_lit[-1] + 2
pos_cge_ticks = np.append(pos_cge_ticks, pos_cge_ref)
cge_ticklabels = cge_lit["study"].to_list()
cge_ticklabels.append("general model")

# Plot
cge_ax.boxplot(
    x=cge_ref_df,
    positions=[pos_cge_ref],
    vert=True,
    whis=[1, 99],
    showfliers=False,
    widths=1,
    medianprops={"color": "black"},
)
sb.scatterplot(
    data=cge_data,
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
cge_ax.set(ylim=(0, 820))
cge_ax.set(ylabel="$\mathregular{g CO_2 eq./kWh}$")

# Title
cge_ax.set_title("CONVENTIONAL")

# Legend
handles, labels = cge_ax.get_legend_handles_labels()
labels[2] = "simplified model:"
cge_ax.legend(handles=handles[1:], labels=labels[1:], loc="upper right")

# Enhanced
# Re-arrange dataframe
ege_s_df_2 = ege_s_df.rename(columns={"10%": "10,15,20%"})
ege_s_df_2 = ege_s_df_2.melt(
    id_vars="study", var_name="simplified model", value_name="carbon footprint"
)
ege_lit = ege_data
ege_lit["type"] = "literature"

# Set positions
pos_ege_lit = np.arange(len(ege_data))
pos_ege_s = np.hstack([pos_ege_lit + dist, pos_ege_lit + dist])
pos_ege_ticks = pos_ege_lit + dist / 2
pos_ege_ref = pos_ege_lit[-1] + 2
pos_ege_ticks = np.append(pos_ege_ticks, pos_ege_ref)
ege_ticklabels = ege_lit["study"].to_list()
ege_ticklabels.append("general model")

# Plot
ege_ax.boxplot(
    x=ege_ref_df,
    positions=[pos_ege_ref],
    vert=True,
    whis=[1, 99],
    showfliers=False,
    widths=1,
    medianprops={"color": "black"},
)
sb.scatterplot(
    data=ege_data,
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
# if ege_ax == ege_ax_low:
#    sb.scatterplot(data=ege_s_df_2, y="carbon footprint", x=pos_ege_s, hue="simplified", ax=ege_ax)
# elif ege_ax == ege_ax_up:
#    sb.stripplot(data=ege_s_df_2, y="carbon footprint", x=pos_ege_s, hue="simplified", ax=ege_ax,
#                 jitter=True)
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
# handles = [handles[1],handles[3], handles[4]]
# labels = [labels[1],labels[3], labels[4]]
labels[2] = "simplified model:"
ege_ax.legend(handles=handles[1:], labels=labels[1:], loc="upper right")

fig.subplots_adjust(hspace=0.010)
fig.set_size_inches([11, 8])
fig.tight_layout()


#%% Save
fig.savefig(os.path.join(folder_OUT, file_name + ".tiff"), dpi=300)


#%% Plot with break on axis - SUBSIDED

sb.set(font_scale=0.6)
sb.set_style("dark")

# Subplots
fig, ((cge_ax_up, ege_ax_up), (cge_ax_low, ege_ax_low)) = plt.subplots(
    nrows=2,
    ncols=2,
    sharex="col",
    gridspec_kw={"width_ratios": [2, 3], "height_ratios": [2, 3]},
)

# Distance between points
dist = 0.3

# Conventional

# Re-arrange dataframe
cge_s_df_2 = cge_s_df.rename(columns={"10%": "all thresholds"})
cge_s_df_2 = cge_s_df_2.melt(
    id_vars="study", var_name="simplified model", value_name="carbon footprint"
)
cge_lit = cge_data
cge_lit["type"] = "literature"

# Set positions
pos_cge_lit = np.arange(len(cge_data))
pos_cge_s = pos_cge_lit + dist
pos_cge_ticks = pos_cge_lit + dist / 2
pos_cge_ref = pos_cge_lit[-1] + 2
pos_cge_ticks = np.append(pos_cge_ticks, pos_cge_ref)
cge_ticklabels = cge_lit["study"].to_list()
cge_ticklabels.append("general model")

# Plot
for cge_ax in [cge_ax_up, cge_ax_low]:
    cge_ax.boxplot(
        x=cge_ref_df,
        positions=[pos_cge_ref],
        vert=True,
        whis=[1, 99],
        showfliers=False,
        widths=1,
        medianprops={"color": "black"},
    )
    sb.scatterplot(
        data=cge_data,
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
    cge_ax.tick_params(axis="x", which="both", labelrotation=90, labelsize=8)
    cge_ax.get_legend().remove()

# y-axis limits
cge_ax_up.set(ylim=(370, 820))
cge_ax_low.set(ylim=(0, 320))
cge_ax_low.set(ylabel="$\mathregular{g CO_2 eq./kWh}$")

# Title
cge_ax_up.set_title("CONVENTIONAL", fontsize=10)

# Legend
handles, labels = cge_ax.get_legend_handles_labels()
labels[2] = "simplified model:"
cge_ax_up.legend(handles=handles[1:], labels=labels[1:], loc="upper right")

# Enhanced
# Re-arrange dataframe
ege_s_df_2 = ege_s_df.rename(columns={"10%": "10,15,20%"})
ege_s_df_2 = ege_s_df_2.melt(
    id_vars="study", var_name="simplified model", value_name="carbon footprint"
)
ege_lit = ege_data
ege_lit["type"] = "literature"

# Set positions
pos_ege_lit = np.arange(len(ege_data))
pos_ege_s = np.hstack([pos_ege_lit + dist, pos_ege_lit + dist])
pos_ege_ticks = pos_ege_lit + dist / 2
pos_ege_ref = pos_ege_lit[-1] + 2
pos_ege_ticks = np.append(pos_ege_ticks, pos_ege_ref)
ege_ticklabels = ege_lit["study"].to_list()
ege_ticklabels.append("general model")

# Plot
for ege_ax in [ege_ax_up, ege_ax_low]:
    ege_ax.boxplot(
        x=ege_ref_df,
        positions=[pos_ege_ref],
        vert=True,
        whis=[1, 99],
        showfliers=False,
        widths=1,
        medianprops={"color": "black"},
    )
    sb.scatterplot(
        data=ege_data,
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
    # if ege_ax == ege_ax_low:
    #    sb.scatterplot(data=ege_s_df_2, y="carbon footprint", x=pos_ege_s, hue="simplified", ax=ege_ax)
    # elif ege_ax == ege_ax_up:
    #    sb.stripplot(data=ege_s_df_2, y="carbon footprint", x=pos_ege_s, hue="simplified", ax=ege_ax,
    #                 jitter=True)
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
    ege_ax.tick_params(axis="x", labelrotation=90, labelsize=8)
    ege_ax.get_legend().remove()

# Limits
ege_ax_up.set(ylim=(370, 820))
ege_ax_low.set(ylim=(0, 320))
ege_ax_low.set(ylabel="$\mathregular{g CO_2 eq./kWh}$")

# Title
ege_ax_up.set_title("ENHANCED", fontsize=10)

handles, labels = ege_ax.get_legend_handles_labels()
# handles = [handles[1],handles[3], handles[4]]
# labels = [labels[1],labels[3], labels[4]]
labels[2] = "simplified model:"
ege_ax_up.legend(handles=handles[1:], labels=labels[1:], loc="upper right", fontsize=7)

fig.subplots_adjust(hspace=0.010)
fig.set_size_inches([11, 6])
fig.tight_layout()

# Change label position at the end in order not to change the format
ege_ax_low.yaxis.set_label_coords(-0.06, 1)
cge_ax_low.yaxis.set_label_coords(-0.09, 1)
