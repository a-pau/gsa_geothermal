import brightway2 as bw
import seaborn as sb
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib import ticker

# Local files
from gsa_geothermal.data import (
    get_df_carbon_footprints_from_literature_conventional,
    get_df_carbon_footprints_from_literature_enhanced
)


if __name__ == '__main__':
    # Set project
    bw.projects.set_current("Geothermal")

    # Method
    ILCD_CC = [
        method
        for method in bw.methods
        if "ILCD 2.0 2018 midpoint no LT" in str(method)
        and "climate change total" in str(method)
    ]

    # Carbon footprints from literature

    conventional_cfs = get_df_carbon_footprints_from_literature_conventional()
    conventional_cfs = conventional_cfs.drop(
        columns=[
            "Technology",
            "Notes",
            "Operational CO2 emissions (g/kWh)",
            "Operational CH4 emissions (g/kWh)",
        ]
    )
    conventional_cfs.columns = ["study", "carbon footprint"]

    enhanced_cfs = get_df_carbon_footprints_from_literature_enhanced()
    enhanced_cfs = enhanced_cfs.drop(
        columns=[
            "Technology",
            "Notes",
            "Diesel consumption (GJ/m)",
            "Installed capacity (MW)",
            "Depth of wells (m)",
            "Success rate (%)",
        ]
    )
    enhanced_cfs.columns = ["study", "carbon footprint"]

    # Reference model carbon footprints
    n_iter = 10000
    ecoinvent_version = "ecoinvent_3.6"
    folder_IN = os.path.join("generated_files", ecoinvent_version, "validation")
    file_name = "ReferenceVsLiterature CC N" + str(n_iter)

    cge_ref_df = pd.read_json(
        os.path.join(absolute_path, folder_IN, file_name + " - Conventional")
    )
    ege_ref_df = pd.read_json(
        os.path.join(absolute_path, folder_IN, file_name + " - Enhanced")
    )

    # Seaborn palette
    Sb_colorblind_pal = sb.color_palette(palette="colorblind")
    Color_brewer_Set2 = sb.color_palette(palette="Set2")
    Color_brewer_Paired = sb.color_palette(palette="Paired")
    palette = Color_brewer_Paired
    palette.append(Color_brewer_Set2[-1])

    # Add columns for plotting with stripplot
    enhanced_cfs["position"] = 1
    conventional_cfs["position"] = 1

    #%% Conventional model plot
    fig = plt.figure()
    fig.add_subplot(121)

    g1 = sb.boxplot(
        data=cge_ref_df,
        y="carbon footprint",
        whis=[1, 99],
        showfliers=False,
        width=0.02,
        color="white",
    )
    g1 = sb.stripplot(
        data=conventional_cfs,
        x="position",
        y="carbon footprint",
        palette=palette[:11],
        hue="study",
        s=6,
        jitter=0.01,
    )

    handles, labels = g1.get_legend_handles_labels()
    g1.legend(
        handles=handles,
        labels=labels,
        loc="upper right",
        fontsize=7,
        markerscale=0.5,
        frameon=False,
    )

    # For "original" plot remove yscale
    g1.set(
        title="CONVENTIONAL",
        xlabel="",
        ylabel="$g CO_2 eq./kWh$",
        xlim=(-0.015, 0.05),
        ylim=(5, 1000),
        yscale="log",
    )
    g1.set_xticks([])
    g1.get_yaxis().set_major_formatter(ticker.ScalarFormatter())

    #%%  Enhanced model Plot
    fig.add_subplot(122)
    g2 = sb.boxplot(
        data=ege_ref_df,
        y="carbon footprint",
        whis=[1, 99],
        showfliers=False,
        width=0.02,
        color="white",
    )
    g2 = sb.stripplot(
        data=enhanced_cfs,
        x="position",
        y="carbon footprint",
        palette=palette[:13],
        hue="study",
        s=6,
        jitter=0.01,
    )

    handles, labels = g2.get_legend_handles_labels()
    g2.legend(
        handles=handles,
        labels=labels,
        loc="upper right",
        fontsize=7,
        markerscale=0.5,
        frameon=False,
    )

    # For "original" plot remove ylim and yscale
    g2.set(
        title="ENHANCED",
        xlabel="",
        ylabel="",
        xlim=(-0.015, 0.05),
        ylim=(5, 1000),
        yscale="log",
    )
    g2.set_xticks([])
    g2.get_yaxis().set_major_formatter(ticker.ScalarFormatter())

    #%% Layout
    sb.despine(fig=fig, bottom=True)
    fig.set_size_inches([8, 4])
    fig.tight_layout()

    #%% Save plots

    folder_OUT = os.path.join(absolute_path, "generated_plots", ecoinvent_version)
    fig.savefig(os.path.join(folder_OUT, file_name + ".tiff"), dpi=300)

    #%% Conventional plot - Violin

    cge_1 = pd.DataFrame(cge_ref_df["carbon footprint"])
    cge_1["type"] = "model"
    cge_2 = pd.DataFrame(conventional_cfs["carbon footprint"])
    cge_2["type"] = "literature"
    cge = pd.concat([cge_1, cge_2], ignore_index=True)
    cge["x"] = "x"

    f3 = plt.figure()
    g3 = sb.violinplot(
        data=cge,
        x="x",
        y="carbon footprint",
        hue="type",
        split=True,
        inner="quartile",
        cut=0,
    )

    handles, labels = g3.get_legend_handles_labels()
    g3.legend(handles=handles[0:], labels=labels[0:], loc="upper right", fontsize=9)

    g3.set(xlabel="", ylabel="$g CO_2 eq./kWh$", ylim=(0))
    g3.set_xticks([])

    #%% Enhanced plot - Violin

    ege_1 = pd.DataFrame(ege_ref_df["carbon footprint"])
    ege_1["type"] = "model"
    ege_2 = pd.DataFrame(enhanced_cfs["carbon footprint"])
    ege_2["type"] = "literature"
    ege = pd.concat([ege_1, ege_2], ignore_index=True)
    ege["x"] = "x"

    f4 = plt.figure()
    g4 = sb.violinplot(
        data=ege,
        x="x",
        y="carbon footprint",
        hue="type",
        split=True,
        inner="quartile",
        cut=0,
    )

    handles, labels = g4.get_legend_handles_labels()
    g4.legend(handles=handles[0:], labels=labels[0:], loc="upper right", fontsize=9)

    g4.set(xlabel="", ylabel="$g CO_2 eq./kWh$", ylim=(0))
    g4.set_xticks([])

    #%% Save Violin
    folder_OUT = os.path.join(absolute_path, "generated_plots", ecoinvent_version)

    f3.savefig(
        os.path.join(folder_OUT, file_name + " - Conventional VIOLIN.png"),
        dpi=600,
        format="png",
    )
    f4.savefig(
        os.path.join(folder_OUT, file_name + " - Enhanced VIOLIN.png"),
        dpi=600,
        format="png",
    )
