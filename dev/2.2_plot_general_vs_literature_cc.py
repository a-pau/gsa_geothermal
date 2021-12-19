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
from gsa_geothermal.plotting.utils import make_handle


if __name__ == '__main__':
    # Set project
    bw.projects.set_current("Geothermal")

    # Method
    method = get_EF_methods(select_climate_change_only=True)

    # Number of iterations
    iterations = 10000
    seed = 13413203

    # Save data
    write_dir = Path("write_files") / "validation"
    write_dir_figures = write_dir / "figures"
    write_dir_figures.mkdir(parents=True, exist_ok=True)
    filename_conventional_scores = "{}.general.climate_change.N{}.seed{}.json".format("conventional", iterations, seed)
    filepath_conventional_scores = write_dir / filename_conventional_scores
    filename_enhanced_scores = "{}.general.climate_change.N{}.seed{}.json".format("enhanced", iterations, seed)
    filepath_enhanced_scores = write_dir / filename_enhanced_scores

    # Load carbon footprints from literature
    df_conventional_literature = get_df_carbon_footprints_from_literature_conventional()
    df_conventional_literature = df_conventional_literature.drop(
        columns=[
            "Technology",
            "Notes",
            "Operational CO2 emissions (g/kWh)",
            "Operational CH4 emissions (g/kWh)",
        ]
    )
    df_conventional_literature.columns = ["study", "carbon footprint", "model"]

    df_enhanced_literature = get_df_carbon_footprints_from_literature_enhanced()
    df_enhanced_literature = df_enhanced_literature.drop(
        columns=[
            "Technology",
            "Notes",
            "Diesel consumption (GJ/m)",
            "Installed capacity (MW)",
            "Depth of wells (m)",
            "Success rate (%)",
        ]
    )
    df_enhanced_literature.columns = ["study", "carbon footprint", "model"]

    # Load general model scores
    df_conventional_general = pd.read_json(filepath_conventional_scores)
    df_enhanced_general = pd.read_json(filepath_enhanced_scores)

    # Seaborn palette
    Sb_colorblind_pal = sb.color_palette(palette="colorblind")
    Color_brewer_Set2 = sb.color_palette(palette="Set2")
    Color_brewer_Paired = sb.color_palette(palette="Paired")
    palette = Color_brewer_Paired
    palette.extend(Color_brewer_Set2[-4:])

    # Add columns for plotting with stripplot
    df_enhanced_literature["position"] = 1
    df_conventional_literature["position"] = 1
    
    # Order dataframe
    df_conventional_literature.sort_values(by="model", inplace=True)
    df_enhanced_literature.sort_values(by="model", inplace=True)

    # number of generic models
    num_gen_conv = len(df_conventional_literature[df_conventional_literature["model"]=="generic"])
    num_gen_enh = len( df_enhanced_literature[df_enhanced_literature["model"]=="generic"])

    # %% BOX PLOT
    
    fig = plt.figure()
    
    # CONVENTIONAL
    
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
        data=df_conventional_literature[df_conventional_literature["model"] == "generic"],
        x="position",
        y="carbon footprint",
        palette=palette[0:num_gen_conv],
        hue="study",
        s=6,
        jitter=0.01,
        marker="o"
    )
    
    g1 = sb.stripplot(
        data=df_conventional_literature[df_conventional_literature["model"] == "site-specific"],
        x="position",
        y="carbon footprint",
        palette=palette[num_gen_conv:len(df_conventional_literature)],
        hue="study",
        s=6,
        jitter=0.01,
        marker="^"
    )

    #handles, labels = g1.get_legend_handles_labels()
    handles_new = make_handle(
        num_gen_conv, 
        len(df_conventional_literature), 
        palette
    )
    g1.legend(
        handles=handles_new,
        labels=df_conventional_literature["study"].to_list(),
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

    # ENHANCED
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
        data=df_enhanced_literature[df_enhanced_literature["model"] == "generic"],
        x="position",
        y="carbon footprint",
        palette=palette[0:num_gen_enh],
        hue="study",
        s=6,
        jitter=0.01,
        marker="o"
    )
    
    g2 = sb.stripplot(
        data=df_enhanced_literature[df_enhanced_literature["model"] == "site-specific"],
        x="position",
        y="carbon footprint",
        palette=palette[num_gen_enh:len(df_enhanced_literature)],
        hue="study",
        s=6,
        jitter=0.01,
        marker="^"
    )


    handles_new = make_handle(
        num_gen_enh, 
        len(df_enhanced_literature), 
        palette
    )
    
    g2.legend(
        handles=handles_new,
        labels=df_enhanced_literature["study"].to_list(),
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

    # Fix layout
    sb.despine(fig=fig, bottom=True)
    fig.set_size_inches([8, 4])
    fig.tight_layout()
 
    #%% Save plot
    filename_plot = "{}.tiff".format(filepath_conventional_scores.stem.replace("conventional.", ""))
    filepath_plot = write_dir_figures / filename_plot
    print ("Saving {}".format(filepath_plot))
    fig.savefig( filepath_plot, dpi=300)


    # # %% VIOLIN PLOT - not used in paper
    # # NOTE: no model-specific labels) 

    # # Conventional
    # cge_1 = pd.DataFrame(df_conventional_general["carbon footprint"])
    # cge_1["type"] = "model"
    # cge_2 = pd.DataFrame(df_conventional_literature["carbon footprint"])
    # cge_2["type"] = "literature"
    # cge = pd.concat([cge_1, cge_2], ignore_index=True)
    # cge["x"] = "x"

    # f3 = plt.figure()
    # g3 = sb.violinplot(
    #     data=cge,
    #     x="x",
    #     y="carbon footprint",
    #     hue="type",
    #     split=True,
    #     inner="quartile",
    #     cut=0,
    # )

    # handles, labels = g3.get_legend_handles_labels()
    # g3.legend(handles=handles[0:], labels=labels[0:], loc="upper right", fontsize=9)

    # g3.set(xlabel="", ylabel="$g CO_2 eq./kWh$", ylim=0)
    # g3.set_xticks([])

    # # Enhanced
    # ege_1 = pd.DataFrame(df_enhanced_general["carbon footprint"])
    # ege_1["type"] = "model"
    # ege_2 = pd.DataFrame(df_enhanced_literature["carbon footprint"])
    # ege_2["type"] = "literature"
    # ege = pd.concat([ege_1, ege_2], ignore_index=True)
    # ege["x"] = "x"

    # f4 = plt.figure()
    # g4 = sb.violinplot(
    #     data=ege,
    #     x="x",
    #     y="carbon footprint",
    #     hue="type",
    #     split=True,
    #     inner="quartile",
    #     cut=0,
    # )

    # handles, labels = g4.get_legend_handles_labels()
    # g4.legend(handles=handles[0:], labels=labels[0:], loc="upper right", fontsize=9)

    # g4.set(xlabel="", ylabel="$g CO_2 eq./kWh$", ylim=0)
    # g4.set_xticks([])

    # # Save Violin
    # f3.savefig(
    #     write_dir_figures / "{}.violin.png".format(filepath_conventional_scores.stem),
    #     dpi=600,
    #     format="png",
    # )
    # f4.savefig(
    #   write_dir_figures / "{}.violin.png".format(filepath_enhanced_scores.stem),
    #   dpi=600,
    #       format="png",
    # )
