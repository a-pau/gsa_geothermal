#%% Set up and load data
import brightway2 as bw
import seaborn as sb
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

# Set working directory
path = "."
os.chdir(path)
absolute_path = os.path.abspath(path)

# Set project
bw.projects.set_current("Geothermal")

# Method 
ILCD_CC = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)]

# Carbon footprints from literature
cge_cfs=pd.read_excel(os.path.join(absolute_path, "data_and_models/Carbon footprints from literature.xlsx"), sheet_name="Conventional", index_col=None, skiprows=1)
cge_cfs=cge_cfs.drop(columns=["Technology", "Notes", "Operational CO2 emissions (g/kWh)"])
cge_cfs.columns= ["study", "carbon footprint"]

ege_cfs=pd.read_excel(os.path.join(absolute_path, "data_and_models/Carbon footprints from literature.xlsx"), sheet_name="Enhanced", index_col=None, skiprows=1)
ege_cfs=ege_cfs.drop(columns=["Technology", "Notes", "Diesel consumption (GJ/m)", "Installed capacity (MW)"])
ege_cfs.columns= ["study", "carbon footprint"]

# Reference model carbon footprints
n_iter = 10000
ecoinvent_version = "ecoinvent_3.6"
file_name="ReferenceVsLiterature CC N" + str(n_iter)
cge_ref_df = pd.read_json(os.path.join(absolute_path, "generated_files", "validation_" + ecoinvent_version, file_name + " - Conventional"))
ege_ref_df = pd.read_json(os.path.join(absolute_path, "generated_files", "validation_" + ecoinvent_version, file_name + " - ENhanced"))

#%% Reference model plot

f1=plt.figure()
g1=sb.boxplot(data=cge_ref_df, y="carbon footprint", whis=[5,95], showfliers=True, width=0.3)
g1=sb.scatterplot(data=cge_cfs, x=0.5, y="carbon footprint", hue="study")

handles, labels = g1.get_legend_handles_labels()
g1.legend(handles=handles[1:], labels=labels[1:])

g1.set(xlabel='', ylabel='$gCO_2-eq./kWh$')
g1.set_xticks([])

#%%  Enhanced model Plot

f2=plt.figure()
sb.boxplot(data=ege_ref_df, y="carbon footprint",whis=[5,95], showfliers=True, width=0.3)
g2=sb.scatterplot(data=ege_cfs, x=0.5, y="carbon footprint", hue="study")

handles, labels = g2.get_legend_handles_labels()
g2.legend(handles=handles[1:], labels=labels[1:])

g2.set(xlabel='', ylabel='$gCO_2-eq./kWh$')
g2.set_xticks([])

#%% Save plots

#Options not enabled 
#file_name = get_file_name("cge_ReferenceModel_validation.png", exploration=exploration, success_rate=success_rate)
#file_name = get_file_name("ege_ReferenceModel_validation.png", exploration=exploration, success_rate=success_rate)

f1.savefig(os.path.join(absolute_path, "generated_plots", "validation_" + ecoinvent_version, file_name + " - Conventional.png"), dpi=600, format="png")
f2.savefig(os.path.join(absolute_path, "generated_plots", "validation_" + ecoinvent_version, file_name+" - Enhanced.png"), dpi=600, format="png")
