#%% Set-up
import seaborn as sb
import matplotlib.pyplot as plt
import pandas as pd
import os 
from utils.FileNameFromOptions import get_file_name
import textwrap

# Set working directory
path = "."
os.chdir(path)
absolute_path = os.path.abspath(path)

#%% Choose option

exploration = True
success_rate = True

#%% Load data
n_iter = 1000
file_name =get_file_name("ReferenceVsSimplified_test_cases CC", exploration=exploration, success_rate=success_rate) 
file_name = file_name + " N" + str(n_iter)

cge_ref_df = pd.read_json(os.path.join(absolute_path, "generated_files", file_name + " - Conventional Ref")) \
            .melt(var_name="study", value_name="carbon footprint")
cge_s_df = pd.read_json(os.path.join(absolute_path, "generated_files", file_name + " - Conventional Sim")) \
            .melt(var_name="study", value_name="carbon footprint")
ege_ref_df = pd.read_json(os.path.join(absolute_path, "generated_files", file_name + " - Enhanced Ref")) \
            .melt(var_name="study", value_name="carbon footprint")
ege_s_df = pd.read_json(os.path.join(absolute_path, "generated_files", file_name + " - Enhanced Sim")) \
            .melt(var_name="study", value_name="carbon footprint")

#%% Conventional 

# Load literature carbon footprints and operational co2 emissions
cge_cfs=pd.read_excel(os.path.join(absolute_path, "data_and_models/Carbon footprints from literature.xlsx"), sheet_name="Conventional", index_col=None, skiprows=1)
cge_cfs=cge_cfs.dropna(subset=["Operational CO2 emissions (g/kWh)"])

cge_s_and_lit_df = pd.DataFrame.merge(cge_s_df, cge_cfs, left_on="study", right_on="Study").drop(columns=["Study", "Notes", "Technology", "Operational CO2 emissions (g/kWh)"])
cge_s_and_lit_df.columns=["study", "simplified model", "literature"]
cge_s_and_lit_df=cge_s_and_lit_df.melt(id_vars="study", var_name="type", value_name="carbon footprint")

cge_study_list = cge_cfs.Study.tolist()

# This script plots carbon footprints from simplified model and from literature as
# categorical variable (ie "dodged") on top of boxplot generated by the reference model
# 
# Stripplot enables categorical plotting of scatterplot
# We need to iterate of axes so that we can change labels and reset legend

cge_plot, cge_ax = plt.subplots(2, 4)

for counter, study_ in enumerate(cge_study_list):
    if counter <= 3:
        i= counter
        j=0
    elif counter >3:
        i= counter-4
        j=1
    sb.boxplot(data=cge_ref_df[cge_ref_df.study==study_], x="study", y="carbon footprint", color="white", showfliers=False, whis=[5,95], ax=cge_ax[j][i])
    sb.stripplot(data=cge_s_and_lit_df[cge_s_and_lit_df.study==study_], x="study", y= "carbon footprint", hue="type", jitter=False, dodge=True, ax=cge_ax[j][i])
    cge_ax[j][i].set_xlabel("")
    cge_ax[j][i].set_xticks([],[])
    cge_ax[j][i].set_title(textwrap.fill(study_,30) + "\n")
    cge_ax[j][i].get_legend().remove() 
            
    if i != 0:
        cge_ax[j][i].set_ylabel("")
    elif i == 0:
        cge_ax[j][i].set_ylabel(r"$g CO{2} eq./ kWh$")
        
handles, labels = cge_ax[0][0].get_legend_handles_labels()
cge_plot.legend(handles, labels, loc='upper center', ncol=2)

#%% Enhanced

# Load literature carbon footprints and operational co2 emissions
ege_cfs=pd.read_excel(os.path.join(absolute_path, "data_and_models/Carbon footprints from literature.xlsx"), sheet_name="Enhanced", index_col=None, skiprows=1, nrows=10)

ege_s_and_lit_df = pd.DataFrame.merge(ege_s_df, ege_cfs, left_on="study", right_on="Study").drop(columns=["Study", "Notes", "Technology", "Diesel consumption (GJ/m)", "Installed capacity (MW)" ])
ege_s_and_lit_df.columns=["study", "simplified model", "literature"]
ege_s_and_lit_df=ege_s_and_lit_df.melt(id_vars="study", var_name="type", value_name="carbon footprint")

ege_study_list = ege_cfs.Study.tolist()

# This script plots carbon footprints from simplified model and from literature as
# categorical variable (ie "dodged") on top of boxplot generated by the reference model
# 
# Stripplot enables categorical plotting of scatterplot
# We need to iterate of cge_axes so that we can change labels and reset legend

ege_plot, ege_ax = plt.subplots(2, 5)

for counter, study_ in enumerate(ege_study_list):
    if counter <= 4:
        i= counter
        j=0
    elif counter >4:
        i= counter-5
        j=1
    sb.boxplot(data=ege_ref_df[ege_ref_df.study==study_], x="study", y="carbon footprint", color="white", showfliers=False, whis=[5,95], ax=ege_ax[j][i])
    sb.stripplot(data=ege_s_and_lit_df[ege_s_and_lit_df.study==study_], x="study", y= "carbon footprint", hue="type", jitter=False, dodge=True, ax=ege_ax[j][i])
    ege_ax[j][i].set_xlabel("")
    ege_ax[j][i].set_xticks([],[])
    ege_ax[j][i].set_title(textwrap.fill(study_,30) + "\n")
    ege_ax[j][i].get_legend().remove() 
       
    if i != 0:
        ege_ax[j][i].set_ylabel("")
    elif i == 0:
        ege_ax[j][i].set_ylabel(r"$g CO{2} eq./ kWh$")
        
handles, labels = ege_ax[0][0].get_legend_handles_labels()
ege_plot.legend(handles, labels, loc='upper center', ncol=2)

#%% Save plots

file_name = get_file_name("ReferenceVsSmplified_test_cases", exploration=exploration, success_rate=success_rate)
file_name = file_name + " N" + str(n_iter)
cge_plot.savefig(os.path.join(absolute_path, "generated_plots", file_name + " - Conventional.png"), dpi=600, format="png")
ege_plot.savefig(os.path.join(absolute_path, "generated_plots", file_name + " - Enhanced.png"), dpi=600, format="png")