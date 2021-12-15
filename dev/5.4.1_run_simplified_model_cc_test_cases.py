# %% Set-up
import bw2data as bd
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
from matplotlib.ticker import FormatStrFormatter
from pathlib import Path

# Import local
from gsa_geothermal.utils import get_EF_methods
from gsa_geothermal.data import (
    get_df_carbon_footprints_from_literature_conventional,
    get_df_carbon_footprints_from_literature_enhanced
)
from gsa_geothermal.simplified_models import ConventionalSimplifiedModel, EnhancedSimplifiedModel
from setups import setup_geothermal_gsa

if __name__ == '__main__':
    # Set project
    bd.projects.set_current("Geothermal")

    # Method
    method = get_EF_methods(select_climate_change_only=True)

    write_dir_plots = Path("write_plots")

    # Path to MC scores
    iterations_gsa = 500
    path_scores_conv = Path("write_files") / "conventional.N{}".format(iterations_gsa) / "scores"
    path_scores_enh = Path("write_files") / "enhanced.N{}".format(iterations_gsa) / "scores"

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

    # Load literature data
    df_conventional_literature = get_df_carbon_footprints_from_literature_conventional()
    df_enhanced_literature = get_df_carbon_footprints_from_literature_enhanced()
    df_conventional_literature = df_conventional_literature.dropna(
        subset=["Operational CO2 emissions (g/kWh)"]
    ).reset_index(
        drop=True
    )
    # df_conventional_literature = df_conventional_literature.iloc[[4,5,6,7]]
    df_conventional_literature = df_conventional_literature[df_conventional_literature.columns[[0, 2, 3]]]
    df_conventional_literature.columns = ["study", "carbon footprint", "co2_emissions"]
    df_conventional_literature["co2_emissions"] = df_conventional_literature["co2_emissions"] / 1000
    df_conventional_literature = df_conventional_literature.sort_values(by="study")

    df_enhanced_literature = df_enhanced_literature[df_enhanced_literature.columns[[0, 2, 3, 4, 5, 6]]]
    df_enhanced_literature.columns = [
        "study",
        "carbon footprint",
        "specific_diesel_consumption",
        "installed_capacity",
        "average_depth_of_wells",
        "success_rate_primary_wells",
    ]
    df_enhanced_literature["specific_diesel_consumption"] = df_enhanced_literature["specific_diesel_consumption"] * 1000
    df_enhanced_literature = df_enhanced_literature.sort_values(by="study")

    # %% Initialize classes
    # Set threshold, note that only these thresholds are needed for CC
    thresholds_cge = [0.1]
    thresholds_ege = [0.1, 0.05]

    # Conventional
    cge_model_s = {}
    for threshold in thresholds_cge:
        cge_model_s[threshold] = ConventionalSimplifiedModel(
            setup_geothermal_gsa,
            path_scores_conv,
            threshold,
        )

    # Enhanced
    ege_model_s = {}
    for threshold in thresholds_ege:
        ege_model_s[threshold] = EnhancedSimplifiedModel(
            setup_geothermal_gsa,
            path_scores_enh,
            threshold,
        )

    # %% Compute simplified

    # Conventional
    cge_s = {}
    for threshold in thresholds_cge:
        temp_ = {}
        for _, rows in df_conventional_literature.iterrows():
            # Values are multplied by 1000 to get gCO2 eq
            temp_[rows["study"]] = (
                cge_model_s[threshold].run(rows, lcia_methods=method)[method[0][-2]] * 1000
            )
        cge_s[threshold] = temp_

    # Re-arrange results
    cge_s_df = pd.DataFrame.from_dict(cge_s)
    cge_s_df.columns = ["{:.0%}".format(t) for t in cge_s_df.columns]
    cge_s_df = cge_s_df.reset_index().rename(columns={"index": "study"})

    # Enhanced
    ege_s = {}
    for t in thresholds_ege:
        temp_ = {}
        for _, rows in df_enhanced_literature.iterrows():
            # Values are multplied by 1000 to get gCO2 eq
            temp_[rows["study"]] = (
                ege_model_s[t].run(rows, lcia_methods=method)[method[0][-2]] * 1000
            )
        ege_s[t] = temp_

    # Re-arrange results
    ege_s_df = pd.DataFrame.from_dict(ege_s)
    ege_s_df.columns = ["{:.0%}".format(t) for t in ege_s_df.columns]
    ege_s_df = ege_s_df.reset_index().rename(columns={"index": "study"})

    # %% Plot

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
    cge_ax.set(ylim=(0, 820))
    cge_ax.set(ylabel=r"$\mathregular{g CO_2 eq./kWh}$")

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
    ege_ax.set(ylabel=r"$\mathregular{g CO_2 eq./kWh}$")

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

    # %% Save
    fig.savefig(write_dir_plots / "a.tiff", dpi=300)  # TODO Andrea rename this figure

    # %% Plot with break on axis - SUBSIDED

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
    for cge_ax in [cge_ax_up, cge_ax_low]:
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
        cge_ax.tick_params(axis="x", which="both", labelrotation=90, labelsize=8)
        cge_ax.get_legend().remove()

    # y-axis limits
    cge_ax_up.set(ylim=(370, 820))
    cge_ax_low.set(ylim=(0, 320))
    cge_ax_low.set(ylabel=r"$\mathregular{g CO_2 eq./kWh}$")

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
    for ege_ax in [ege_ax_up, ege_ax_low]:
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
    ege_ax_low.set(ylabel=r"$\mathregular{g CO_2 eq./kWh}$")

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
