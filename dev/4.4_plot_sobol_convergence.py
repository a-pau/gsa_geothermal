import pandas as pd
from pathlib import Path
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Local files
from gsa_geothermal.plotting.utils import *
from setups import setup_geothermal_gsa
from gsa_geothermal.utils import get_lcia_results
from gsa_geothermal.global_sensitivity_analysis import my_sobol_analyze


if __name__ == "__main__":

    option = "enhanced.diff_distributions"
    iterations = 500

    # Define paths and load data
    path_base = Path("write_files") / "{}.N{}".format(option, iterations)
    path_scores = path_base / "scores"
    scores = get_lcia_results(path_scores)

    # Setup everything
    problem, calc_second_order, parameters_list, methods = setup_geothermal_gsa(option)
    first_df = pd.read_excel(path_base / "sobol_first.xlsx")
    total_df = pd.read_excel(path_base / "sobol_total.xlsx")

    first_df_prepared = prepare_df(first_df, option)
    n_parameters = len(first_df)
    parameters = first_df["parameters"].values
    parameters_ordered = first_df_prepared["level_0"].values
    parameters = [parameters_dict.get(p) or p for p in parameters]
    parameters_ordered = [parameters_dict.get(p) or p for p in parameters_ordered]

    methods_names = [methods_dict.get(m[-2]) for m in methods]

    iterations_start = 2
    iterations_end = iterations
    iterations_step = iterations // 100  # 4032

    Ns = np.arange(iterations_start, iterations_end, iterations_step)

    first_arr = np.zeros((Ns.shape[0], len(methods), n_parameters))
    total_arr = np.zeros((Ns.shape[0], len(methods), n_parameters))

    for i, n in enumerate(Ns):

        first_methods = {}
        total_methods = {}
        num_runs = n * (n_parameters + 2)
        scores_n = scores[:num_runs]

        for j, m in enumerate(methods_names):
            sa_dict = my_sobol_analyze(
                problem, scores_n[:, j], calc_second_order=calc_second_order
            )
            first = sa_dict["S1"]
            total = sa_dict["ST"]
            first_arr[i, j] = abs(first)
            total_arr[i, j] = total

    df_first = pd.DataFrame(index=methods_names, columns=parameters)
    df_total = pd.DataFrame(index=methods_names, columns=parameters)

    for j, m in enumerate(methods_names):
        for k, p in enumerate(parameters):
            df_first.loc[m][p] = first_arr[:, j, k]
            df_total.loc[m][p] = total_arr[:, j, k]

    df_first = df_first[parameters_ordered]
    df_total = df_total[parameters_ordered]

    flatten = lambda l: [item for sublist in l for item in sublist]
    subplots_titles = [["FIRST ORDER " + m, "TOTAL ORDER " + m] for m in methods_names]

    # Make colors transparent
    opacity = 1.0
    colors_opaque = {
        name: rgb[:3] + "a" + rgb[3:-1] + "," + str(opacity) + ")"
        for name, rgb in colors.items()
    }

    m_start = 0
    m_end = 8

    n_rows = m_end - m_start
    n_cols = 2
    fig = make_subplots(
        rows=n_rows,
        cols=n_cols,
        subplot_titles=flatten(subplots_titles[m_start:m_end]),
    )

    how_many_params = 4

    flag = True
    for i, method in enumerate(methods_names[m_start:m_end]):
        df_first_row = df_first.loc[method]
        df_total_row = df_total.loc[method]

        for j in range(how_many_params):

            name_ = df_first_row.index[j]

            fig.add_trace(
                go.Scatter(
                    x=Ns[1:],
                    y=df_first_row[j][1:],
                    name=name_,
                    mode="lines+markers",
                    marker=dict(
                        size=4,
                        symbol="circle",
                        opacity=opacity,
                    ),
                    line=dict(color=colors_opaque[name_], width=2),
                    showlegend=False,
                ),
                row=i + 1,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=Ns[1:],
                    y=df_total_row[j][1:],
                    name=df_first_row.index[j],
                    mode="lines+markers",
                    marker=dict(
                        size=4,
                        symbol="circle",
                        opacity=opacity,
                    ),
                    line=dict(color=colors_opaque[name_], width=2),
                    showlegend=flag,
                ),
                row=i + 1,
                col=2,
            )
            fig.update_layout(
                font_size=18,
                font_family="Arial",
                margin=dict(l=20, r=20, t=40, b=20),
                font_color="black",
            )
        flag = False
        max_val = np.max(
            [
                1,
                max(np.array([df_j[1:] for df_j in df_total_row]).flatten()),
                max(np.array([df_j[1:] for df_j in df_first_row]).flatten()),
            ]
        )
        range_ = np.arange(0, max_val + 0.8, 1)
        for k in range(2):
            fig["layout"]["yaxis" + str(i * 2 + k + 1)].update(
                range=[-0.2, max(range_) + 0.2], tickvals=range_, ticktext=range_
            )

    fig.update_layout(
        height=1600,
        width=1130,
        legend=dict(x=0.1, y=-0.02, orientation="h"),
        plot_bgcolor=plot_bgcolor_,
    )

    for i in fig["layout"]["annotations"]:
        i["font"]["size"] = 22
        i["font"]["color"] = "black"
        i["font"]["family"] = "Arial"

    fig.show()

    # Save image
    path_figures = path_base / "figures"
    path_figures.mkdir(parents=True, exist_ok=True)
    filepath = path_figures / "sobol_convergence_robust_{}_{}_params{}_{}.pdf".format(
        m_start, m_end, how_many_params, option
    )
    fig.write_image(filepath)
