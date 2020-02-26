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
folder_IN = os.path.join("generated_files", ecoinvent_version, "validation")
file_name="ReferenceVsLiterature CC N" + str(n_iter)

cge_ref_df = pd.read_json(os.path.join(absolute_path, folder_IN, file_name + " - Conventional"))
ege_ref_df = pd.read_json(os.path.join(absolute_path, folder_IN, file_name + " - Enhanced"))

# Seaborn palette
Sb_colorblind_pal= sb.color_palette(palette="colorblind", n_colors=10)
Color_brewer_Set2 = sb.color_palette(palette="Set2")
Sb_colorblind_pal.append(Color_brewer_Set2[0])

#%% Conventional model plot

f1=plt.figure()
g1=sb.boxplot(data=cge_ref_df, y="carbon footprint", whis=[1,99], showfliers=False, width=0.02)
g1=sb.scatterplot(data=cge_cfs, x=0.03, y="carbon footprint", palette=Sb_colorblind_pal, hue="study", s=65)

handles, labels = g1.get_legend_handles_labels()
g1.legend(handles=handles[1:], labels=labels[1:], loc='upper right', fontsize=7)

g1.set(xlabel='', ylabel='$g CO_2 eq./kWh$', xlim=(-0.015,0.1))
g1.set_xticks([])


#%%  Enhanced model Plot

f2=plt.figure()
sb.boxplot(data=ege_ref_df, y="carbon footprint",whis=[1,99], showfliers=False, width=0.02)
g2=sb.scatterplot(data=ege_cfs, x=0.03, y="carbon footprint", palette=Sb_colorblind_pal, hue="study", s=65)

handles, labels = g2.get_legend_handles_labels()
g2.legend(handles=handles[1:], labels=labels[1:], loc='upper right', fontsize=7)

g2.set(xlabel='', ylabel='$g CO_2 eq./kWh$', xlim=(-0.015,0.1))
g2.set_xticks([])

#%% Tight layout
f1.tight_layout()
f2.tight_layout()

#%% Save plots

#Options not enabled 
#file_name = get_file_name("cge_ReferenceModel_validation.png", exploration=exploration, success_rate=success_rate)
#file_name = get_file_name("ege_ReferenceModel_validation.png", exploration=exploration, success_rate=success_rate)

folder_OUT = os.path.join(absolute_path, "generated_plots", ecoinvent_version)

f1.savefig(os.path.join(folder_OUT, file_name + " - Conventional.png"), dpi=600, format="png")
f2.savefig(os.path.join(folder_OUT, file_name + " - Enhanced.png"), dpi=600, format="png")
