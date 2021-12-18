#%% Set-up
import bw2data as bd
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
from matplotlib import patches
import textwrap
from pathlib import Path

# from local files
from gsa_geothermal.utils import get_EF_methods

# Set project
bd.projects.set_current("Geothermal")

# Retrieve methods
methods, methods_units = get_EF_methods(return_units=True)

# Load general model MC scores
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
    pd.read_json(filepath_conventional_general)
    ).melt(var_name="method", value_name="impact")

df_general_model_enh = (
        pd.read_json(filepath_enhanced_general)
        ).melt(var_name="method", value_name="impact")

# Load literature scores
filename_hellisheidi_lit = "{}_impacts.xlsx".format("hellisheidi")
filepath_hellisheidi_lit = write_dir_validation / filename_hellisheidi_lit
df_hellisheidi_lit = pd.read_excel(
    filepath_hellisheidi_lit,
    sheet_name="Sheet1",
    index_col=0,
    usecols=[0, 2, 4],
).rename(columns={"method_2": "method"})

filename_uddgp_lit = "{}_impacts.xlsx".format("uddgp")
filepath_uddgp_lit = write_dir_validation / filename_uddgp_lit
df_uddgp_lit = pd.read_excel(
    filepath_uddgp_lit,
    sheet_name="Sheet1",
    index_col=0,
    usecols=[0, 2, 4],
).rename(columns={"method_2": "method"})

# option
exploration_uddgp = False

# Load simplified model scores
filename_hellisheidi_simplified = "simplified_model.{}.json".format("hellisheidi")
filepath_hellisheidi_simplified = write_dir_validation / filename_hellisheidi_simplified
df_hellisheidi_simplified = pd.read_json(filepath_hellisheidi_simplified)

df_uddgp_simplified = {}
for exploration in [True, False]:
    filename_uddgp_simplified = "simplified_model.{}.exploration_{}.json".format("uddgp", exploration)
    filepath_uddgp_simplified = write_dir_validation/ filename_uddgp_simplified
    df_uddgp_simplified[str(exploration)] = pd.read_json(filepath_uddgp_simplified)

# Plot options
sb.set_style("darkgrid")
sb.set_context(
    rc={
        "axes.titlesize": 13,
        "axes.labelsize": 13,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,
    }
)
sb_pal = sb.color_palette()

# Save data
write_dir_figures = Path("write_files") / "validation" / "figures"

#%% Conventional plot

# Re-arrange dataframes
cge_s_df_20 = df_hellisheidi_simplified[["method", "20%"]].rename(columns={"20%": "impact"})
cge_s_df_15 = df_hellisheidi_simplified[["method", "15%"]].rename(columns={"15%": "impact"})
cge_s_df_10 = df_hellisheidi_simplified[["method", "10%"]].rename(columns={"10%": "impact"})
cge_s_df_5 = df_hellisheidi_simplified[["method", "5%"]].rename(columns={"5%": "impact"})

df_hellisheidi_lit["pos"] = 1 - 0.4
cge_s_df_20["pos"] = 1 - 0.2
cge_s_df_15["pos"] = 1
cge_s_df_10["pos"] = 1 + 0.2
cge_s_df_5["pos"] = 1 + 0.4

# Plot
cge_plot, cge_ax = plt.subplots(2, 8)
for counter, method_ in enumerate(methods):
    if counter <= 7:
        i = counter
        j = 0
    elif counter > 7:
        i = counter - 8
        j = 1

    ref_temp = df_general_model_conv[df_general_model_conv.method == method_[1]]
    temp_hellisheidi_sco = df_hellisheidi_lit[df_hellisheidi_lit["method"] == method_[1]]
    temp_s_20 = cge_s_df_20[cge_s_df_20["method"] == method_[1]]
    temp_s_15 = cge_s_df_15[cge_s_df_15["method"] == method_[1]]
    temp_s_10 = cge_s_df_10[cge_s_df_10["method"] == method_[1]]
    temp_s_5 = cge_s_df_5[cge_s_df_5["method"] == method_[1]]

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
        x=temp_hellisheidi_sco.pos,
        y=temp_hellisheidi_sco.impact,
        c="black",
        marker="s",
        label="literature",
    )
    cge_ax[j][i].scatter(x=temp_s_20.pos, y=temp_s_20.impact, c=sb_pal[0], label="20%")
    cge_ax[j][i].scatter(x=temp_s_15.pos, y=temp_s_15.impact, c=sb_pal[1], label="15%")
    cge_ax[j][i].scatter(x=temp_s_10.pos, y=temp_s_10.impact, c=sb_pal[2], label="10%")
    cge_ax[j][i].scatter(x=temp_s_5.pos, y=temp_s_5.impact, c=sb_pal[3], label="5%")

    cge_ax[j][i].set_xlabel("")
    cge_ax[j][i].set_ylabel(methods_units[counter])
    cge_ax[j][i].set_xticks([], [])
    cge_ax[j][i].set_title(textwrap.fill(method_[1][:-6], 15) + "\n")
    cge_ax[j][i].ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
    cge_ax[j][i].set_xlim(0.5, 1.5)

# Legend
# empty handle
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

# save plot
filename_plot_hellisheidi = (
    "simplified_vs_general.hellisheidi.N{}.tiff".format(iterations)
)
filepath_plot_hellisheidi = write_dir_figures / filename_plot_hellisheidi
print("Saving {}".format(filepath_plot_hellisheidi))
cge_plot.savefig(filepath_plot_hellisheidi, dpi=300)


#%% Enhanced plot

for exploration in [True, False]:

    # Re-arrange dataframes
    ege_s_df_20 = df_uddgp_simplified[str(exploration)][["method", "20%"]].rename(columns={"20%": "impact"})
    ege_s_df_15 = df_uddgp_simplified[str(exploration)][["method", "15%"]].rename(columns={"15%": "impact"})
    ege_s_df_10 = df_uddgp_simplified[str(exploration)][["method", "10%"]].rename(columns={"10%": "impact"})
    ege_s_df_5 = df_uddgp_simplified[str(exploration)][["method", "5%"]].rename(columns={"5%": "impact"})
    
    df_uddgp_lit["pos"] = 1 - 0.4
    ege_s_df_20["pos"] = 1 - 0.2
    ege_s_df_15["pos"] = 1
    ege_s_df_10["pos"] = 1 + 0.2
    ege_s_df_5["pos"] = 1 + 0.4
    
    # Get Seaborn palette
    sb_pal = sb.color_palette()
    
    # Plot
    ege_plot, ege_ax = plt.subplots(2, 8)
    for counter, method_ in enumerate(methods):
        if counter <= 7:
            i = counter
            j = 0
        elif counter > 7:
            i = counter - 8
            j = 1
    
        ref_temp = df_general_model_enh[df_general_model_enh.method == method_[1]]
        temp_UDDGP_sco = df_uddgp_lit[df_uddgp_lit["method"] == method_[1]]
        temp_s_20 = ege_s_df_20[ege_s_df_20["method"] == method_[1]]
        temp_s_15 = ege_s_df_15[ege_s_df_15["method"] == method_[1]]
        temp_s_10 = ege_s_df_10[ege_s_df_10["method"] == method_[1]]
        temp_s_5 = ege_s_df_5[ege_s_df_5["method"] == method_[1]]
    
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
        ege_ax[j][i].set_ylabel(methods_units[counter])
        ege_ax[j][i].set_xticks([], [])
        ege_ax[j][i].set_title(textwrap.fill(method_[1][:-6], 15) + "\n")
        ege_ax[j][i].ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
        ege_ax[j][i].set_xlim(0.5, 1.5)
    
    # Legend
    # empty handle
    emp_han = patches.Rectangle((0, 0), 1, 1, fill=False, edgecolor="none", visible=False)
    handles, labels = ege_ax[0][0].get_legend_handles_labels()
    box_han = patches.Rectangle((0, 0), 1, 2, fill=False, edgecolor="black")
    handles.insert(0, box_han)
    labels.insert(0, "general model")
    handles.insert(2, emp_han)
    labels.insert(2, "simplified model:")
    
    if exploration:
        ege_plot.suptitle("UNITED DOWNS GEOTHERMAL POWER PLANT", fontsize=15)
    else:
        ege_plot.suptitle(
            "UNITED DOWNS GEOTHERMAL POWER PLANT, NO EXPLORATION", fontsize=15
        )
    
    ege_plot.legend(handles, labels, loc="lower center", ncol=7)
    ege_plot.subplots_adjust(wspace=0, hspace=0.4)
    ege_plot.set_size_inches([14, 8])
    ege_plot.tight_layout(rect=[0, 0.05, 1, 0.95])

    # save plot
    filename_plot_uddgp = (
        "simplified_vs_general.uddgp.exploration_{}.N{}.tiff".format(exploration, iterations)
    )
    filepath_plot_uddgp = write_dir_figures / filename_plot_uddgp
    print("Saving {}".format(filepath_plot_uddgp))
    ege_plot.savefig(filepath_plot_uddgp, dpi=300)