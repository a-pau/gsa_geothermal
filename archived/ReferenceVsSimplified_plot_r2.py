#%% Set up and load data
import brightway2 as bw
import seaborn as sb
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

# Import local
from setup_files_gsa import get_ILCD_methods

# Set working directry
path = "."
os.chdir(path)
absolute_path = os.path.abspath(path)

# Set project
bw.projects.set_current("Geothermal")

# Methods
ILCD, ILCD_units = get_ILCD_methods(units=True)

# Iterations
n_iter = 10000

# Folders
file_name = "ReferenceVsSimplified_N" + str(n_iter)
ecoinvent_version = "ecoinvent_3.6"
folder_IN = os.path.join(
    absolute_path, "generated_files", ecoinvent_version, "validation"
)
folder_OUT = os.path.join(absolute_path, "generated_plots", ecoinvent_version)

# Thresholds
threshold = [0.2, 0.15, 0.1, 0.05]

# Reference
cge_ref_df = pd.read_json(
    os.path.join(folder_IN, file_name + "_Conventional_Reference")
).melt(var_name="method", value_name="Reference")
ege_ref_df = pd.read_json(
    os.path.join(folder_IN, file_name + "_Enhanced_Reference")
).melt(var_name="method", value_name="Reference")

cge_s_df = {}
ege_s_df = {}
for t in threshold:
    cge_s_df[t] = pd.read_json(
        os.path.join(folder_IN, file_name + "_Conventional_Simplified_t" + str(t))
    ).melt(var_name="method", value_name="Simplified_" + str(t))
    ege_s_df[t] = pd.read_json(
        os.path.join(folder_IN, file_name + "_Enhanced_Simplified_t" + str(t))
    ).melt(var_name="method", value_name="Simplified_" + str(t))

cge_df = cge_ref_df
ege_df = ege_ref_df
for t in threshold:
    cge_df = pd.concat([cge_df, cge_s_df[t]["Simplified_" + str(t)]], axis=1)
    ege_df = pd.concat([ege_df, ege_s_df[t]["Simplified_" + str(t)]], axis=1)

#%%  Calculate coefficient of determination

cge_r_squared = {}
cge_r_squared_adj = {}
# n_par = {0.2: 2, 0.15:2, 0.1:3}
for method in ILCD:
    df = cge_df[cge_df.method == method[2]]
    temp = {}
    # temp2 = {}
    for t in threshold:
        SS_Residual = sum((df["Reference"] - df["Simplified_" + str(t)]) ** 2)
        SS_Total = sum((df["Reference"] - df["Reference"].mean()) ** 2)
        temp[t] = 1 - (float(SS_Residual)) / SS_Total
        # temp2[t] = 1 - (1 - temp[t]) * (17-1)/(17-1-n_par[t])
    cge_r_squared[method[2]] = temp
    # cge_r_squared_adj[method[2]] = temp2

cge_r_squared_df = pd.DataFrame.from_dict(cge_r_squared, orient="index")
cge_r_squared_df.columns = ["{:.0%}".format(t) for t in cge_r_squared_df.columns]

# cge_r_squared_adj_df = pd.DataFrame.from_dict(cge_r_squared_adj, orient="index")
# cge_r_squared_adj_df.columns = ["{:.0%}".format(t) for t in cge_r_squared_adj_df.columns]

ege_r_squared = {}
for method in ILCD:
    df = ege_df[ege_df.method == method[2]]
    temp = {}
    for t in threshold:
        SS_Residual = sum((df["Reference"] - df["Simplified_" + str(t)]) ** 2)
        SS_Total = sum((df["Reference"] - df["Reference"].mean()) ** 2)
        temp[t] = 1 - (float(SS_Residual)) / SS_Total
    ege_r_squared[method[2]] = temp

ege_r_squared_df = pd.DataFrame.from_dict(ege_r_squared, orient="index")
ege_r_squared_df.columns = ["{:.0%}".format(t) for t in ege_r_squared_df.columns]

#%% Plot

sb.set_style("darkgrid")

fig, (cge_plot, ege_plot) = plt.subplots(nrows=1, ncols=2, sharey=True)

# CONVENTIONAL
# Rearrange dataframe
cge_r_squared_df_m = cge_r_squared_df.reset_index().rename(columns={"index": "method"})
cge_r_squared_df_m = cge_r_squared_df_m.melt(
    id_vars="method", var_name="threshold", value_name="r_squared"
)

# Plot
sb.stripplot(
    data=cge_r_squared_df_m,
    y="method",
    x="r_squared",
    hue="threshold",
    dodge=True,
    s=6,
    ax=cge_plot,
)
cge_plot.set(
    xlim=(0.55, 1.02), xlabel="$\mathregular{R^2}$", ylabel="", title="CONVENTIONAL"
)
cge_plot.grid(which="major", axis="y")
cge_plot.get_legend().remove()
# handles, labels = cge_plot.get_legend_handles_labels()
# cge_plot.legend(handles, labels, loc='center right', ncol=1)

# ENHANCED
# Rearrange dataframe
ege_r_squared_df_m = ege_r_squared_df.reset_index().rename(columns={"index": "method"})
ege_r_squared_df_m = ege_r_squared_df_m.melt(
    id_vars="method", var_name="threshold", value_name="r_squared"
)

# Plot
sb.stripplot(
    data=ege_r_squared_df_m,
    y="method",
    x="r_squared",
    hue="threshold",
    dodge=True,
    s=6,
    ax=ege_plot,
)
ege_plot.set(
    xlim=(0.55, 1.02), xlabel="$\mathregular{R^2}$", ylabel="", title="ENHANCED"
)
ege_plot.grid(which="major", axis="y")
ege_plot.get_legend().remove()

# Legend
handles, labels = ege_plot.get_legend_handles_labels()
fig.legend(handles, labels, loc=(0.45, 0.02), ncol=4)
fig.set_size_inches([11, 5])
fig.tight_layout(rect=[0, 0.05, 1, 1])

#%% Save
plot_file_name = file_name + "_r2"
fig.savefig(os.path.join(folder_OUT, plot_file_name + ".tiff"), dpi=300)
