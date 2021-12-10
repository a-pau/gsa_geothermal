#%% Set-up
import brightway2 as bw
import pandas as pd
import os
import warnings
import seaborn as sb
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FormatStrFormatter
from matplotlib import patches
import textwrap

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
ILCD, ILCD_units = get_ILCD_methods(units=True)

# Folder and file name for saving
ecoinvent_version = "ecoinvent_3.6"
absolute_path = os.path.abspath(path)
folder_OUT = os.path.join(absolute_path, "generated_plots", ecoinvent_version)
file_name = "ReferenceVsSimplified"

# Parameters
# Hellisheidi
cge_parameters = {
    "co2_emissions": 20.9 / 1000,
    "gross_power_per_well": 9,
    "average_depth_of_wells": 2220,
    "initial_harmonic_decline_rate": 0.03,
    "success_rate_primary_wells": 100,
}

# UDDGP
ege_parameters = {
    "installed_capacity": 1,
    "average_depth_of_wells": 4000,
    "specific_diesel_consumption": 7.2 * 1000,
    "success_rate_primary_wells": 100,
}

# Load reference model
n_iter = 1000
folder_IN = os.path.join(
    absolute_path, "generated_files", ecoinvent_version, "validation"
)
file_name_IN = "ReferenceVsSimplified_N" + str(n_iter)
cge_ref_df = pd.read_json(
    os.path.join(folder_IN, file_name_IN + "_Conventional_Reference")
).melt(var_name="method", value_name="impact")
ege_ref_df = pd.read_json(
    os.path.join(folder_IN, file_name_IN + "_Enhanced_Reference")
).melt(var_name="method", value_name="impact")

# Hellisheidi/UDDGP impacts
folder_IN = os.path.join(absolute_path, "generated_files", ecoinvent_version)
HSD_scores = pd.read_excel(
    os.path.join(folder_IN, "Hellisheidi impacts.xlsx"),
    sheet_name="Sheet1",
    index_col=0,
    usecols=[0, 3, 4],
).rename(columns={"method_3": "method"})

UDDGP_scores = pd.read_excel(
    os.path.join(folder_IN, "UDDGP impacts.xlsx"),
    sheet_name="Sheet1",
    index_col=0,
    usecols=[0, 3, 4],
).rename(columns={"method_3": "method"})

# For plotting
# Get Seaborn palette
sb_pal = sb.color_palette()

# Seaborn style
sb.set_style("darkgrid")

#%% Initialize classes
# Set threshold
threshold = [0.2, 0.15, 0.1, 0.05]

# Exploration is only for ege
exploration = False

cge_model_s = {}
ege_model_s = {}
for t in threshold:
    cge_model_s[t] = cge_model_s_(t)
    ege_model_s[t] = ege_model_s_(t, exploration=exploration)

#%% Compute
cge_s = {}
ege_s = {}
for t in threshold:
    cge_s[t] = cge_model_s[t].run(cge_parameters)
    ege_s[t] = ege_model_s[t].run(ege_parameters)

# Re-arrange results
cge_s_df = pd.DataFrame.from_dict(cge_s)
cge_s_df.columns = ["{:.0%}".format(t) for t in cge_s_df.columns]
cge_s_df = cge_s_df.reset_index().rename(columns={"index": "method"})

ege_s_df = pd.DataFrame.from_dict(ege_s)
ege_s_df.columns = ["{:.0%}".format(t) for t in ege_s_df.columns]
ege_s_df = ege_s_df.reset_index().rename(columns={"index": "method"})

#%% Conventional plot

sb.set_context(
    rc={
        "axes.titlesize": 13,
        "axes.labelsize": 13,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,
    }
)


# Re-arrange dataframes
cge_s_df_20 = cge_s_df[["method", "20%"]].rename(columns={"20%": "impact"})
cge_s_df_15 = cge_s_df[["method", "15%"]].rename(columns={"15%": "impact"})
cge_s_df_10 = cge_s_df[["method", "10%"]].rename(columns={"10%": "impact"})
cge_s_df_5 = cge_s_df[["method", "5%"]].rename(columns={"5%": "impact"})

HSD_scores["pos"] = 1 - 0.4
cge_s_df_20["pos"] = 1 - 0.2
cge_s_df_15["pos"] = 1
cge_s_df_10["pos"] = 1 + 0.2
cge_s_df_5["pos"] = 1 + 0.4

# Plot
cge_plot, cge_ax = plt.subplots(2, 8)
for counter, method_ in enumerate(ILCD):
    if counter <= 7:
        i = counter
        j = 0
    elif counter > 7:
        i = counter - 8
        j = 1

    ref_temp = cge_ref_df[cge_ref_df.method == method_[2]]
    temp_HSD_sco = HSD_scores[HSD_scores["method"] == method_[2]]
    temp_s_20 = cge_s_df_20[cge_s_df_20["method"] == method_[2]]
    temp_s_15 = cge_s_df_15[cge_s_df_15["method"] == method_[2]]
    temp_s_10 = cge_s_df_10[cge_s_df_10["method"] == method_[2]]
    temp_s_5 = cge_s_df_5[cge_s_df_5["method"] == method_[2]]

    # To set color, check Patch_artist
    cge_ax[j][i].boxplot(
        x=ref_temp.impact,
        positions=[1],
        showfliers=False,
        whis=[1, 99],
        widths=0.9,
        medianprops={"color": "black"},
    )
    cge_ax[j][i].scatter(
        x=temp_HSD_sco.pos,
        y=temp_HSD_sco.impact,
        c="black",
        marker="s",
        label="literature",
    )
    cge_ax[j][i].scatter(x=temp_s_20.pos, y=temp_s_20.impact, c=sb_pal[0], label="20%")
    cge_ax[j][i].scatter(x=temp_s_15.pos, y=temp_s_15.impact, c=sb_pal[1], label="15%")
    cge_ax[j][i].scatter(x=temp_s_10.pos, y=temp_s_10.impact, c=sb_pal[2], label="10%")
    cge_ax[j][i].scatter(x=temp_s_5.pos, y=temp_s_5.impact, c=sb_pal[3], label="5%")

    cge_ax[j][i].set_xlabel("")
    cge_ax[j][i].set_ylabel(ILCD_units[counter])
    cge_ax[j][i].set_xticks([], [])
    cge_ax[j][i].set_title(textwrap.fill(method_[2], 15) + "\n")
    cge_ax[j][i].ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
    cge_ax[j][i].set_xlim(0.5, 1.5)

# Empty handle
emp_han = patches.Rectangle((0, 0), 1, 1, fill=False, edgecolor="none", visible=False)
handles, labels = cge_ax[0][0].get_legend_handles_labels()
box_han = patches.Rectangle((0, 0), 1, 2, fill=False, edgecolor="black")
handles.insert(0, box_han)
labels.insert(0, "general model")
handles.insert(2, emp_han)
labels.insert(2, "simplified model:")
cge_plot.legend(handles, labels, loc="lower center", ncol=7)

cge_plot.suptitle("HELLISHEIDI GEOTHERMAL POWER PLANT", fontsize=15)
cge_plot.subplots_adjust(wspace=0, hspace=0.4)
cge_plot.set_size_inches([14, 8])
cge_plot.tight_layout(rect=[0, 0.05, 1, 0.95])

#%% Enhanced plot

# Re-arrange dataframes
ege_s_df_20 = ege_s_df[["method", "20%"]].rename(columns={"20%": "impact"})
ege_s_df_15 = ege_s_df[["method", "15%"]].rename(columns={"15%": "impact"})
ege_s_df_10 = ege_s_df[["method", "10%"]].rename(columns={"10%": "impact"})
ege_s_df_5 = ege_s_df[["method", "5%"]].rename(columns={"5%": "impact"})

UDDGP_scores["pos"] = 1 - 0.4
ege_s_df_20["pos"] = 1 - 0.2
ege_s_df_15["pos"] = 1
ege_s_df_10["pos"] = 1 + 0.2
ege_s_df_5["pos"] = 1 + 0.4

# Get Seaborn palette
sb_pal = sb.color_palette()

# Plot
ege_plot, ege_ax = plt.subplots(2, 8)
for counter, method_ in enumerate(ILCD):
    if counter <= 7:
        i = counter
        j = 0
    elif counter > 7:
        i = counter - 8
        j = 1

    ref_temp = ege_ref_df[ege_ref_df.method == method_[2]]
    temp_UDDGP_sco = UDDGP_scores[UDDGP_scores["method"] == method_[2]]
    temp_s_20 = ege_s_df_20[ege_s_df_20["method"] == method_[2]]
    temp_s_15 = ege_s_df_15[ege_s_df_15["method"] == method_[2]]
    temp_s_10 = ege_s_df_10[ege_s_df_10["method"] == method_[2]]
    temp_s_5 = ege_s_df_5[ege_s_df_5["method"] == method_[2]]

    ege_ax[j][i].boxplot(
        x=ref_temp.impact,
        positions=[1],
        showfliers=False,
        whis=[1, 99],
        widths=0.9,
        medianprops={"color": "black"},
    )
    ege_ax[j][i].scatter(
        x=temp_UDDGP_sco.pos,
        y=temp_UDDGP_sco.impact,
        c="black",
        marker="s",
        label="literature",
    )
    ege_ax[j][i].scatter(x=temp_s_20.pos, y=temp_s_20.impact, c=sb_pal[0], label="20%")
    ege_ax[j][i].scatter(x=temp_s_15.pos, y=temp_s_15.impact, c=sb_pal[1], label="15%")
    ege_ax[j][i].scatter(x=temp_s_10.pos, y=temp_s_10.impact, c=sb_pal[2], label="10%")
    ege_ax[j][i].scatter(x=temp_s_5.pos, y=temp_s_5.impact, c=sb_pal[3], label="5%")

    ege_ax[j][i].set_xlabel("")
    ege_ax[j][i].set_ylabel(ILCD_units[counter])
    ege_ax[j][i].set_xticks([], [])
    ege_ax[j][i].set_title(textwrap.fill(method_[2], 15) + "\n")
    ege_ax[j][i].ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
    ege_ax[j][i].set_xlim(0.5, 1.5)

# Empty handle
emp_han = patches.Rectangle((0, 0), 1, 1, fill=False, edgecolor="none", visible=False)
handles, labels = ege_ax[0][0].get_legend_handles_labels()
box_han = patches.Rectangle((0, 0), 1, 2, fill=False, edgecolor="black")
handles.insert(0, box_han)
labels.insert(0, "general model")
handles.insert(2, emp_han)
labels.insert(2, "simplified model:")

if exploration:
    ege_plot.suptitle("UNITED DOWNS GEOTHERMAL POWER PLANT", fontsize=15)
elif not exploration:
    ege_plot.suptitle(
        "UNITED DOWNS GEOTHERMAL POWER PLANT, NO EXPLORATION", fontsize=15
    )

ege_plot.legend(handles, labels, loc="lower center", ncol=7)
ege_plot.subplots_adjust(wspace=0, hspace=0.4)
ege_plot.set_size_inches([14, 8])
ege_plot.tight_layout(rect=[0, 0.05, 1, 0.95])

#%% Save
file_name_cge = file_name + "_HSD"
cge_plot.savefig(os.path.join(folder_OUT, file_name_cge + ".tiff"), dpi=300)

file_name_ege = file_name + "_UDDGP"
if exploration:
    ege_plot.savefig(os.path.join(folder_OUT, file_name_ege + ".tiff"), dpi=300)
elif not exploration:
    ege_plot.savefig(
        os.path.join(folder_OUT, file_name_ege + "_NO-EXPL" + ".tiff"), dpi=300
    )


#%% Conventional model plots - COULD NOT INSERTE MARKER TYPE IN STRIPPLOT

# # Re-arrange

# cge_s_and_lit_df = pd.merge(cge_s_df, HSD_scores[["method","impact"]], left_on="method", right_on="method")\
#     .rename(columns={"impact":"literature"})
# cge_s_and_lit_df.columns = ["method", "literature", "20%", "15%", "10%", "5%"]
# cge_s_and_lit_df = cge_s_and_lit_df.melt(id_vars="method", var_name="type", value_name="impact")

# # This is to plot the legend for the boxplot too
# cge_ref_df["model"] = "general model"

# cge_plot, cge_ax = plt.subplots(2, 8)
# for counter, method_ in enumerate(ILCD):
#     if counter <= 7:
#         i= counter
#         j=0
#     elif counter >7:
#         i= counter-8
#         j=1
#     sb.boxplot(data=cge_ref_df[cge_ref_df.method==method_[2]], x="method", y="impact",
#                hue="model", color="white", showfliers=False, whis=[1,99], ax=cge_ax[j][i])
#     sb.stripplot(data=cge_s_and_lit_df[cge_s_and_lit_df.method==method_[2]], x="method",
#                  y= "impact", hue="type", jitter=False, dodge=True, s=7, ax=cge_ax[j][i],
#                  marker="s")
#     cge_ax[j][i].set_xlabel("")
#     cge_ax[j][i].set_ylabel(ILCD_units[counter])
#     cge_ax[j][i].set_xticks([],[])
#     cge_ax[j][i].set_title(textwrap.fill(method_[2],15) + "\n")
#     cge_ax[j][i].get_legend().remove()
#     cge_ax[j][i].ticklabel_format(style='sci', axis='y', scilimits=(0,0))

# handles, _ = cge_ax[0][0].get_legend_handles_labels()
# labels=["general model", "simplified model", "Hellisheidi"]
# cge_plot.legend(handles, labels, loc='upper left', ncol=3)

# cge_plot.subplots_adjust(wspace=0, hspace=0.4)
# cge_plot.set_size_inches([14,  8])
# cge_plot.tight_layout(rect=[0,0,1,0.95])
