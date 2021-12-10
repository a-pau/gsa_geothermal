import pandas as pd
from pathlib import Path
from plotly.subplots import make_subplots

# Local files
from gsa_geothermal.plotting.utils import *


if __name__ == "__main__":

    option = "conventional.diff_distributions"
    iterations = 500

    # Load data and setup everything
    path_base = Path("write_files") / "{}.N{}".format(option, iterations)

    first_df = pd.read_excel(path_base / "sobol_first.xlsx", )
    total_df = pd.read_excel(path_base / "sobol_total.xlsx")

    fig = make_subplots(
        rows=1,
        cols=2,
        shared_yaxes=True,
        horizontal_spacing=0.035,
        subplot_titles=("FIRST ORDER SOBOL'", "TOTAL ORDER SOBOL'"),
    )

    flag_leg = True

    for j, first_or_total in enumerate(["first", "total"]):
        if first_or_total == 'first':
            df = prepare_df(first_df, option)
        else:
            df = prepare_df(total_df, option)

        ydata = df.columns[1:].tolist()

        if "conventional" in option:
            range_ = [0, 1.4]
            tickvals_ = [0, 0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4]
            ticktext_ = [0, 0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4]
        elif "enhanced" in option:
            range_ = [0, 1.4]
            tickvals_ = [0, 0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4]
            ticktext_ = [0, 0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4]

        for i in df.index:

            xdata = df.loc[i][1:].tolist()
            name = df.loc[i][0]

            fig.add_bar(
                name=name,
                x=xdata,
                y=ydata,
                orientation="h",
                marker_color=colors[name],
                row=1,
                col=j + 1,
                showlegend=flag_leg,
            )
        fig.update_xaxes(
            range=range_, tickmode="array", tickvals=tickvals_, ticktext=ticktext_
        )

        fig.update_layout(
            barmode="stack",
            font_size=18,
            width=1600,
            height=510,
            legend_traceorder="normal",
            yaxis=dict(autorange="reversed"),
            font_family="Georgia",
            margin=dict(l=0, r=0, t=30, b=10),
            font_color="black",
            plot_bgcolor=plot_bgcolor_,
        )

        flag_leg = False

    fig["layout"]["annotations"][0]["font"]["size"] = 24
    fig["layout"]["annotations"][1]["font"]["size"] = 24

    fig.show()

    # Save image
    path_figures = path_base / "figures"
    path_figures.mkdir(parents=True, exist_ok=True)
    filepath = path_figures / "{}.pdf".format(first_or_total)
    fig.write_image(filepath)
