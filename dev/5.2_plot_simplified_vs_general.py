# %% SETUP

import bw2data as bd
import seaborn as sb
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from scipy.stats import gaussian_kde as kde

# Local files
from gsa_geothermal.utils import get_EF_methods
from gsa_geothermal.plotting.utils import set_axlims

if __name__ == "__main__":
    # Set project
    bd.projects.set_current("Geothermal")

    # Methods
    methods, methods_units = get_EF_methods(return_units=True)

    # Options
    iterations = 10000
    seed = 13413203
    threshold_cge = 0.1  # TODO Need to make this recursive for all thresholds
    threshold_ege = 0.1

    # Load data
    write_dir_validation = Path("write_files") / "validation"
    filename_conventional_general = "{}.{}.all_categories.N{}.seed{}.json".format(
        "conventional", "general", iterations, seed,
    )
    filename_enhanced_general = "{}.{}.all_categories.N{}.seed{}.json".format(
        "enhanced", "general", iterations, seed
    )
    filename_conventional_simplified = (
        "{}.{}.t{:02d}.all_categories.N{}.seed{}.json".format(
            "conventional",
            "simplified",
            int(threshold_cge * 100),
            iterations,
            seed,
        )
    )
    filename_enhanced_simplified = (
        "{}.{}.t{:02d}.all_categories.N{}.seed{}.json".format(
            "enhanced",
            "simplified",
            int(threshold_ege * 100),
            iterations,
            seed,
        )
    )
    filepath_conventional_general = write_dir_validation / filename_conventional_general
    filepath_enhanced_general = write_dir_validation / filename_enhanced_general
    filepath_conventional_simplified = (
        write_dir_validation / filename_conventional_simplified
    )
    filepath_enhanced_simplified = write_dir_validation / filename_enhanced_simplified

    cge_gen_df = pd.read_json(filepath_conventional_general).melt(
        var_name="method", value_name="general"
    )
    ege_gen_df = pd.read_json(filepath_enhanced_general).melt(
        var_name="method", value_name="general"
    )
    cge_s_df = pd.read_json(filepath_conventional_simplified).melt(
        var_name="method", value_name="simplified"
    )
    ege_s_df = pd.read_json(filepath_enhanced_simplified).melt(
        var_name="method", value_name="simplified"
    )

    cge_df = pd.concat([cge_gen_df, cge_s_df["simplified"]], axis=1)
    ege_df = pd.concat([ege_gen_df, ege_s_df["simplified"]], axis=1)

    # save data
    write_dir = Path("write_plots")
    write_dir.mkdir(parents=True, exist_ok=True)

    # %% PARITY PLOT (coloured according to density) - CONVENTIONAL

    sb.set_style("darkgrid")
    sb.set_context(
        rc={
            "axes.titlesize": 11,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
        }
    )

    cge_parityplot_col = plt.figure()
    for i, method in enumerate(methods):
        ax_ = cge_parityplot_col.add_subplot(4, 4, i + 1)
        df = cge_df[cge_df.method == method[1]]

        # Calculate kde density values
        df_ = df[["general", "simplified"]].to_numpy().T
        kde_v = kde(df[["general", "simplified"]].to_numpy().T).evaluate(df_)

        # Sort kde value and df values by kde values
        kde_sort = kde_v.argsort()
        df_sort = df.iloc[kde_sort]
        kde_v_sort = kde_v[kde_sort]

        # Find axis limits
        x_lim = set_axlims(df.general, 0.02)
        y_lim = set_axlims(df.simplified, 0.02)
        lim = (0, max(x_lim[1], y_lim[1]))

        # Parity plot
        sb.lineplot(x=[0, 1e10], y=[0, 1e10], color="black", ax=ax_, linewidth=1)
        plt.scatter(
            x=df_sort.general,
            y=df_sort.simplified,
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

        # Amend other features
        plt.xlim(lim)
        plt.ylim(lim)
        ax_.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))
        title_ = methods[i][2] + "\n" + "[" + methods_units[i] + "]"
        ax_.set_title(label=title_, pad=15)
        ax_.set(xlabel="", ylabel="")
    cge_parityplot_col.text(
        0.5, 0.01, "general model", ha="center", fontsize=12, fontweight="bold"
    )
    cge_parityplot_col.text(
        0.01,
        0.5,
        "simplified model",
        va="center",
        rotation="vertical",
        fontsize=12,
        fontweight="bold",
    )

    # cge_parityplot_col.subplots_adjust(wspace=0.1, hspace=0.6)

    # save plots
    filename_cge_plot = (
        "parity_plot.simplified_vs_general.{}.N{}.threshold{}.tiff".format(
            "conventional", iterations, threshold_cge
        )
    )
    filepath_cge_plot = write_dir / filename_cge_plot
    print("Saving {}".format(filepath_cge_plot))
    cge_parityplot_col.savefig(filepath_cge_plot, dpi=300)

    # %% PARITY PLOT (coloured according to density) - ENHANCED

    ege_parityplot_col = plt.figure()
    for i, method in enumerate(methods):
        ax_ = ege_parityplot_col.add_subplot(4, 4, i + 1)
        df = ege_df[ege_df.method == method[1]]

        # Calculate kde density values
        df_ = df[["general", "simplified"]].to_numpy().T
        kde_v = kde(df[["general", "simplified"]].to_numpy().T).evaluate(df_)

        # Sort kde value and df values by kde values
        kde_sort = kde_v.argsort()
        df_sort = df.iloc[kde_sort]
        kde_v_sort = kde_v[kde_sort]

        # Find axis limits
        x_lim = set_axlims(df.general, 0.02)
        y_lim = set_axlims(df.simplified, 0.02)
        lim = (0, max(x_lim[1], y_lim[1]))

        # Parity plot
        sb.lineplot(x=[0, 1e10], y=[0, 1e10], color="black", ax=ax_, linewidth=1)
        plt.scatter(
            x=df_sort.general,
            y=df_sort.simplified,
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

        # Amend other features
        plt.xlim(lim)
        plt.ylim(lim)
        ax_.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))
        title_ = methods[i][2] + "\n" + "[" + methods_units[i] + "]"
        ax_.set_title(label=title_, pad=15)
        ax_.set(xlabel="", ylabel="")
    ege_parityplot_col.text(
        0.5, 0.01, "general model", ha="center", fontsize=12, fontweight="bold"
    )
    ege_parityplot_col.text(
        0.01,
        0.5,
        "simplified model",
        va="center",
        rotation="vertical",
        fontsize=12,
        fontweight="bold",
    )

    cge_parityplot_col.suptitle(
        "CONVENTIONAL, THRESHOLD=" + "{:.0%}".format(threshold_cge), fontsize=13
    )
    ege_parityplot_col.suptitle(
        "ENHANCED, THRESHOLD=" + "{:.0%}".format(threshold_ege), fontsize=13
    )

    cge_parityplot_col.set_size_inches([13, 13])
    ege_parityplot_col.set_size_inches([13, 13])
    cge_parityplot_col.tight_layout(rect=[0.02, 0.02, 1, 0.95])
    ege_parityplot_col.tight_layout(rect=[0.02, 0.02, 1, 0.95])

    # ege_parityplot_col.subplots_adjust(wspace=0.1, hspace=0.6)

    # Save figures plots # TODO Andrea, don't know if we should add seed to filenames of figures
    filename_ege_plot = (
        "parity_plot.simplified_vs_general.{}.N{}.threshold{}.tiff".format(
            "enhanced", iterations, threshold_cge
        )
    )
    filepath_ege_plot = write_dir / filename_ege_plot
    print("Saving {}".format(filepath_ege_plot))
    ege_parityplot_col.savefig(filepath_ege_plot, dpi=300)

    # %% OTHER PLOTS NOT USED IN PAPER

    # BOX PLOT

    # Re-arrange dataframe
    cge_df_2 = cge_df.melt(id_vars="method", var_name="model", value_name="score")

    cge_boxplot = sb.catplot(
        data=cge_df_2,
        x="model",
        y="score",
        col="method",
        kind="box",
        whis=[5, 95],
        col_wrap=4,
        sharex=True,
        sharey=False,
        showfliers=False,
        height=4,
    )
    for counter, ax in enumerate(cge_boxplot.axes.flatten()):
        ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
        ax.set(xlabel="", title=methods[counter][2])
    # cge_boxplot.fig.tight_layout()
    cge_boxplot.fig.subplots_adjust(hspace=0.3, wspace=0.25, top=0.90)
    cge_boxplot.fig.suptitle("CONVENTIONAL - THRESHOLD " + str(threshold_cge), size=12)

    ege_df2 = ege_df.melt(id_vars="method", var_name="model", value_name="score")
    ege_boxplot = sb.catplot(
        data=ege_df2,
        x="model",
        y="score",
        col="method",
        kind="box",
        whis=[5, 95],
        col_wrap=4,
        sharex=True,
        sharey=False,
        showfliers=False,
    )
    for counter, ax in enumerate(ege_boxplot.axes.flatten()):
        ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
        ax.set(xlabel="", title=methods[counter][2])
    ege_boxplot.fig.subplots_adjust(hspace=0.3, wspace=0.25, top=0.90)
    ege_boxplot.fig.suptitle("ENHANCED - THRESHOLD " + str(threshold_ege), size=12)

    # save plots
    filename_cge_plot_b = (
        "box_plot.simplified_vs_general.{}.N{}.threshold{}.tiff".format(
            "conventional", iterations, threshold_cge
        )
    )
    filepath_cge_plot_b = write_dir / filename_cge_plot_b
    print("Saving {}".format(filepath_cge_plot_b))
    cge_boxplot.savefig(filepath_cge_plot_b, dpi=300)

    filename_ege_plot_b = (
        "box_plot.simplified_vs_general.{}.N{}.threshold{}.tiff".format(
            "enhanced", iterations, threshold_cge
        )
    )
    filepath_ege_plot_b = write_dir / filename_ege_plot_b
    print("Saving {}".format(filepath_ege_plot_b))
    ege_boxplot.savefig(filepath_ege_plot_b, dpi=300)

    # %% Violin plot

    cge_df_3 = cge_df.melt(id_vars="method", var_name="model", value_name="score")
    cge_df_3["temp"] = "temp"

    cge_violinplot = sb.catplot(
        data=cge_df_3,
        x="temp",
        y="score",
        col="method",
        kind="violin",
        hue="model",
        col_wrap=4,
        split=False,
        sharex=False,
        sharey=False,
        legend=False,
    )
    for counter, ax in enumerate(cge_violinplot.axes.flatten()):
        ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
        title_ = methods[counter][2] + "\n" + "[" + methods_units[counter] + "]"
        ax.set(xlabel="", ylabel="", title=title_)
        ax.set_xticks([])
    handles = cge_violinplot._legend_data.values()
    labels = cge_violinplot._legend_data.keys()
    cge_violinplot.fig.subplots_adjust(hspace=0.4, wspace=0.25, bottom=0.1, top=0.9)
    lg_1 = cge_violinplot.fig.legend(
        handles=handles,
        labels=labels,
        loc="center",
        bbox_to_anchor=(0.5, 0.97),
        ncol=2,
        borderaxespad=0.0,
    )

    ege_df_3 = ege_df.melt(id_vars="method", var_name="model", value_name="score")
    ege_df_3["temp"] = "temp"

    ege_violinplot = sb.catplot(
        data=ege_df_3,
        x="temp",
        y="score",
        col="method",
        kind="violin",
        hue="model",
        col_wrap=4,
        split=False,
        sharex=False,
        sharey=False,
        legend=False,
    )
    for counter, ax in enumerate(ege_violinplot.axes.flatten()):
        ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
        title_ = methods[counter][2] + "\n" + "[" + methods_units[counter] + "]"
        ax.set(xlabel="", ylabel="", title=title_)
        ax.set_xticks([])
    handles = ege_violinplot._legend_data.values()
    labels = ege_violinplot._legend_data.keys()
    ege_violinplot.fig.subplots_adjust(hspace=0.4, wspace=0.25, bottom=0.1, top=0.9)
    lg_2 = ege_violinplot.fig.legend(
        handles=handles,
        labels=labels,
        loc="center",
        bbox_to_anchor=(0.5, 0.97),
        ncol=2,
        borderaxespad=0.0,
    )

    cge_violinplot.fig.tight_layout(rect=[0, 0, 1, 0.95])
    ege_violinplot.fig.tight_layout(rect=[0, 0, 1, 0.95])

    # save plot
    filename_cge_plot_v = (
        "violin_plot.simplified_vs_general.{}.N{}.threshold{}.tiff".format(
            "conventional", iterations, threshold_cge
        )
    )
    filepath_cge_plot_v = write_dir / filename_cge_plot_v
    print("Saving {}".format(filepath_cge_plot_v))
    cge_boxplot.savefig(filepath_cge_plot_v, dpi=300)

    filename_ege_plot_v = (
        "violin_plot.simplified_vs_general.{}.N{}.threshold{}.tiff".format(
            "enhanced", iterations, threshold_cge
        )
    )
    filepath_ege_plot_v = write_dir / filename_ege_plot_v
    print("Saving {}".format(filepath_ege_plot_v))
    ege_boxplot.savefig(filepath_ege_plot_v, dpi=300)
