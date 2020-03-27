#%% Set up
import seaborn as sb
import matplotlib.pyplot as plt
import pandas as pd
import os
import brightway2 as bw
from utils.FileNameFromOptions import get_file_name
import textwrap

# Set working directory
path = "."
os.chdir(path)
absolute_path = os.path.abspath(path)

# Set project
bw.projects.set_current("Geothermal")

# Retrieve methods 
ILCD_CC = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)]
ILCD_HH = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "human health" in str(method)]
ILCD_EQ = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "ecosystem quality" in str(method)]
ILCD_RE = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "resources" in str(method)]
ILCD = ILCD_CC + ILCD_HH + ILCD_EQ + ILCD_RE

#%% Choose option
exploration = False
success_rate = False

#%% Load data

ecoinvent_version = "ecoinvent_3.6"

#Hellisheidi/UDDGP impacts
folder_IN = os.path.join(absolute_path,"generated_files", ecoinvent_version)
HSD_scores = pd.read_excel(os.path.join(folder_IN, "Hellisheidi impacts.xlsx"), sheet_name="Sheet1", index_col=0)
UDDGP_scores = pd.read_excel(os.path.join(folder_IN, "UDDGP impacts.xlsx"), sheet_name="Sheet1", index_col=0)

# Reference and conventional model
n_iter = 10000
file_name =get_file_name("ReferenceVsSmplified_UDDGP_and_HSD", exploration=exploration, success_rate=success_rate) 
file_name = file_name + " N" + str(n_iter)
folder_IN_2 = os.path.join(absolute_path, "generated_files", ecoinvent_version, "validation")

cge_ref_df = pd.read_json(os.path.join(folder_IN_2, file_name + " - Conventional Ref"))
cge_s_df = pd.read_json(os.path.join(folder_IN_2, file_name + " - Conventional Sim"))
ege_ref_df = pd.read_json(os.path.join(folder_IN_2, file_name + " - Enhanced Ref"))
ege_s_df = pd.read_json(os.path.join(folder_IN_2, file_name + " - Enhanced Sim"))

cge_s_and_Hellisheidi_df = pd.merge(cge_s_df, HSD_scores[["method_3", "impact"]], left_on="method_3", right_on="method_3")
cge_s_and_Hellisheidi_df=cge_s_and_Hellisheidi_df.rename(columns={"impact":"HSD"})
cge_s_and_Hellisheidi_df=cge_s_and_Hellisheidi_df.drop(columns=["method_1", "method_2"]).melt(id_vars="method_3", var_name="type", value_name="impact score")

ege_s_and_UDDGP_df = pd.merge(ege_s_df, UDDGP_scores[["method_3","impact"]], left_on="method_3", right_on="method_3")
ege_s_and_UDDGP_df = ege_s_and_UDDGP_df.rename(columns={"impact":"UDDGP"})
ege_s_and_UDDGP_df=ege_s_and_UDDGP_df.drop(columns=["method_1", "method_2"]).melt(id_vars="method_3", var_name="type", value_name="impact score")

#%% Conventional model plots

cge_plot, cge_ax = plt.subplots(2, 8)
for counter, method_ in enumerate(ILCD):
    if counter <= 7:
        i= counter
        j=0
    elif counter >7:
        i= counter-8
        j=1
    sb.boxplot(data=cge_ref_df[cge_ref_df.method_3==method_[2]], x="method_3", y="impact score", color="white", showfliers=False, whis=[5,95], ax=cge_ax[j][i])
    sb.stripplot(data=cge_s_and_Hellisheidi_df[cge_s_and_Hellisheidi_df.method_3==method_[2]], x="method_3", y= "impact score", hue="type",jitter=False, dodge=True, ax=cge_ax[j][i])
    cge_ax[j][i].set_xlabel("")
    cge_ax[j][i].set_xticks([],[])
    cge_ax[j][i].set_title(textwrap.fill(method_[2],20) + "\n")
    cge_ax[j][i].get_legend().remove() 
    cge_ax[j][i].ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    
    if i != 0:
        cge_ax[j][i].set_ylabel("")
    elif i == 0:
        cge_ax[j][i].set_ylabel("Impact score")

handles, labels = cge_ax[0][0].get_legend_handles_labels()
cge_plot.legend(handles, labels, loc='upper center', ncol=2) 

#%%First make plot full screen
cge_plot.tight_layout()
cge_plot.subplots_adjust(top=0.85)
           
#%% Enhanced model plots

ege_plot, ege_ax = plt.subplots(2, 8)
for counter, method_ in enumerate(ILCD):
    if counter <= 7:
        i= counter
        j=0
    elif counter >7:
        i= counter-8
        j=1
    sb.boxplot(data=ege_ref_df[cge_ref_df.method_3==method_[2]], x="method_3", y="impact score", color="white", showfliers=False, whis=[5,95], ax=ege_ax[j][i])
    sb.stripplot(data=ege_s_and_UDDGP_df[ege_s_and_UDDGP_df.method_3==method_[2]], x="method_3", y= "impact score", hue="type",jitter=False, dodge=True, ax=ege_ax[j][i])
    ege_ax[j][i].set_xlabel("")
    ege_ax[j][i].set_xticks([],[])
    ege_ax[j][i].set_title(textwrap.fill(method_[2],20) + "\n")
    ege_ax[j][i].get_legend().remove() 
    ege_ax[j][i].ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    
    if i != 0:
        ege_ax[j][i].set_ylabel("")
    elif i == 0:
        ege_ax[j][i].set_ylabel("Impact score")

handles, labels = ege_ax[0][0].get_legend_handles_labels()
ege_plot.legend(handles, labels, loc='upper center', ncol=2) 

#%%First make plot full screen
ege_plot.tight_layout()
ege_plot.subplots_adjust(top=0.85)

#%% Save plots

file_name = get_file_name("ReferenceVsSmplified_UDDGP_and_HSD", exploration=exploration, success_rate=success_rate)
file_name = file_name + " N" + str(n_iter)
folder_OUT = os.path.join(absolute_path, "generated_plots", ecoinvent_version)


print("Saving ", file_name)

cge_plot.savefig(os.path.join(folder_OUT, file_name + " - Conventional.png"), dpi=600, format="png")
ege_plot.savefig(os.path.join(folder_OUT, file_name + " - Enhanced.png"), dpi=600, format="png")
