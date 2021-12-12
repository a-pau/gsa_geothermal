import brightway2 as bw
import seaborn as sb
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib import ticker

# Local files
from gsa_geothermal.data import (
    get_df_carbon_footprints_from_literature_conventional,
    get_df_carbon_footprints_from_literature_enhanced
)
from gsa_geothermal.utils import get_EF_methods


if __name__ == '__main__':
    # Set project
    bw.projects.set_current("Geothermal")

    # Method
    method = get_EF_methods(select_climate_change_only=True)

    # Number of iterations
    iterations = 1000

    # Save data
    write_dir = Path("write_files") / "validation"
    write_dir.mkdir(parents=True, exist_ok=True)
    filename_conventional_scores = "{}.general.climate_change.N{}.json".format("conventional", iterations)
    filepath_conventional_scores = write_dir / filename_conventional_scores
    filename_enhanced_scores = "{}.general.climate_change.N{}.json".format("enhanced", iterations)
    filepath_enhanced_scores = write_dir / filename_enhanced_scores

    # Carbon footprints from literature
    df_conventional_literature = get_df_carbon_footprints_from_literature_conventional()
    df_conventional_literature = df_conventional_literature.drop(
        columns=[
            "Technology",
            "Notes",
            "Operational CO2 emissions (g/kWh)",
            "Operational CH4 emissions (g/kWh)",
            "Type",  # TODO Andrea check if that's correct
        ]
    )
    df_conventional_literature.columns = ["study", "carbon footprint"]

    df_enhanced_literature = get_df_carbon_footprints_from_literature_enhanced()
    df_enhanced_literature = df_enhanced_literature.drop(
        columns=[
            "Technology",
            "Notes",
            "Diesel consumption (GJ/m)",
            "Installed capacity (MW)",
            "Depth of wells (m)",
            "Success rate (%)",
            "Type",  # TODO Andrea check if that's correct
        ]
    )
    df_enhanced_literature.columns = ["study", "carbon footprint"]

    # Reference model carbon footprints
    df_conventional_general = pd.read_json(filepath_conventional_scores)
    df_enhanced_general = pd.read_json(filepath_enhanced_scores)

    # Seaborn palette
    Sb_colorblind_pal = sb.color_palette(palette="colorblind")
    Color_brewer_Set2 = sb.color_palette(palette="Set2")
    Color_brewer_Paired = sb.color_palette(palette="Paired")
    palette = Color_brewer_Paired
    palette.append(Color_brewer_Set2[-1])

    # Add columns for plotting with stripplot
    df_enhanced_literature["position"] = 1
    df_conventional_literature["position"] = 1

    # %% Conventional model plot
    fig = plt.figure()
    fig.add_subplot(121)

    g1 = sb.boxplot(
        data=df_conventional_general,
        y="carbon footprint",
        whis=[1, 99],
        showfliers=False,
        width=0.02,
        color="white",
    )
    g1 = sb.stripplot(
        data=df_conventional_literature,
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

    # %%  Enhanced model Plot
    fig.add_subplot(122)
    g2 = sb.boxplot(
        data=df_enhanced_general,
        y="carbon footprint",
        whis=[1, 99],
        showfliers=False,
        width=0.02,
        color="white",
    )
    g2 = sb.stripplot(
        data=df_enhanced_literature,
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

    # %% Layout
    sb.despine(fig=fig, bottom=True)
    fig.set_size_inches([8, 4])
    fig.tight_layout()

    # %% Save plots

    fig.savefig(
        write_dir / "{}.tiff".format(filepath_conventional_scores.stem.replace("conventional.", "")),
        dpi=300
    )

    # %% Conventional plot - Violin

    cge_1 = pd.DataFrame(df_conventional_general["carbon footprint"])
    cge_1["type"] = "model"
    cge_2 = pd.DataFrame(df_conventional_literature["carbon footprint"])
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

    g3.set(xlabel="", ylabel="$g CO_2 eq./kWh$", ylim=0)
    g3.set_xticks([])

    # %% Enhanced plot - Violin

    ege_1 = pd.DataFrame(df_enhanced_general["carbon footprint"])
    ege_1["type"] = "model"
    ege_2 = pd.DataFrame(df_enhanced_literature["carbon footprint"])
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

    g4.set(xlabel="", ylabel="$g CO_2 eq./kWh$", ylim=0)
    g4.set_xticks([])

    # %% Save Violin
    f3.savefig(
        write_dir / "{}.violin.png".format(filepath_conventional_scores.stem),
        dpi=600,
        format="png",
    )
    f4.savefig(
        write_dir / "{}.violin.png".format(filepath_enhanced_scores.stem),
        dpi=600,
        format="png",
    )
